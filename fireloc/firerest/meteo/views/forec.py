"""
Meteorological Forecast
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import wkt_sanitize

from firerest.utils import check_rqst_param
from firerest.permcls import IsFireloc
from authapi.utils import id_usertype

from meteo.models import MeteoForecast, MeteoVariables
from meteo.models import MeteoForecastValues
from meteo.srl import MeteoForecSrl, MeteoForecValSrl
from logs.srl import LogsMeteoSrl



class ManMeteoForecast(APIView):
    """
    Manage Meteorological Forecast
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        List Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        mforec = MeteoForecast.objects.all()
        srl = MeteoForecSrl(mforec, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/forecasts/',
            'service'  : 'manage-meteo-forecasts',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def post(self, request, format=None):
        """
        Add new Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d = request.data

        pp = ["date", "geom", "timezone", "epsg"]

        _status, http = check_rqst_param(pp, list(d.keys()))

        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        # Get Forecast variables
        _vars = []
        if not _status:
            for k in d:
                if k in pp:
                    continue

                try:
                    varobj = MeteoVariables.objects.get(slug=k)
                    _vars.append(varobj)
                except MeteoVariables.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Variable {k} doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break
                
        #Handling geometry
        if not _status and "geom" in d:
            try:
                d["geom"] = wkt_sanitize(
                    d["geom"],
                    epsg=d["epsg"] if d["epsg"] != 3763 else 3763,
                    reprj=3763 if d["epsg"] != 3763 else None,
                    rgeos=True
                )
            except:
                _status, http = {
                    "code"    : "G02",
                    "message" : "EPSG is not a Coordinate Reference System."
                }, status.HTTP_404_NOT_FOUND
        

        # Record Forecast
        if not _status:
            _tz = pytz.timezone(d["timezone"])
            try:
                date = dt.datetime.strptime(d["date"], '%Y-%m-%d %H:%M:%S')
                d["date"] = _tz.localize(date)

            except:
                _status, http = {
                    "code"    : "E07",
                    "message" :  f"Date has not the right format"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:  
            srl = MeteoForecSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                vdata = [{
                    'forecid' : srl.data['id'],
                    'varid'   : v.id,
                    'value'   : d[v.slug] 
                } for v in _vars]

                srlv = MeteoForecValSrl(data=vdata, many=True)

                if srlv.is_valid(): srlv.save()
        
                response = srl.data

                response["vars"] = srlv.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Meteorological Forecast created."
                }, status.HTTP_201_CREATED
                
            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/forecasts/',
            'service'  : 'manage-meteo-forecasts',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, format=None):
        """
        Delete all Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {"status" : {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }}, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            MeteoForecast.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Meteorological Forecast deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/forecasts/',
            'service'  : 'manage-meteo-forecasts',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr


class ManMeteoForec(APIView):
    """
    Manage a Single Meteorological Observation
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, fid, format=None):
        """
        Get a Single Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None

        try:
            mforec = MeteoForecast.objects.get(pk=fid)
        except MeteoForecast.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Forecast doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MeteoForecSrl(mforec)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/forecast/{str(fid)}/',
            'service'  : 'manage-meteo-forecast',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def put(self, request, fid, format=None):
        """
        Update a Single Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["date", "geom"]

        extattr = [k for k in d if k not in rp and k != "epsg"]

        if "date" in d and "timezone" not in d:
            _status, http = {
                "code"    : "E03",
                "message" : "timezone param is mandatory for datetime Updates."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status and "date" in d:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        
        if not _status and "geom" in d and "epsg" not in d:  
            _status, http = {
                "code"    : "E01",
                "message" : "EPSG param is mandatory for Geometry Updates."
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            try:
                mforec  = MeteoForecast.objects.get(pk=fid)
                srlf    = MeteoForecSrl(mforec)
                srldata = srlf.data

            except MeteoForecast.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "Forecast doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        #Handling geometry
        if not _status and "geom" in d:
            try:
                d["geom"] = wkt_sanitize(
                    d["geom"],
                    epsg=d["epsg"] if d["epsg"] != 3763 else 3763,
                    reprj=3763 if d["epsg"] != 3763 else None,
                    rgeos=True
                )
            except:
                _status, http = {
                    "code"    : "G02",
                    "message" : "EPSG is not Coordinate Reference System."
                }, status.HTTP_404_NOT_FOUND
        
        #Handle Extra variables
        vars = []
        if not _status and len(extattr):
            for attr in extattr:
                try:
                    varobj = MeteoVariables.objects.get(slug=attr)
                    vars.append(varobj)

                except MeteoVariables.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Meteorological Variable {attr} doesn't exist."
                    }, status.HTTP_404_NOT_FOUND

                if _status: break
        
        srl_attr = []
        if not _status and len(vars):
            for var in vars:
                _d = {
                    'varid'   : var.id,
                    'forecid' : fid,
                    'value'   : round(float(d[var.slug]), 5)
                }
                try: 
                    mfv = MeteoForecastValues.objects.get(forecid=fid, varid=var.id)
                    mfvsrl = MeteoForecValSrl(mfv, data=_d)

                    if mfvsrl.is_valid():
                        mfvsrl.save()

                        srl_attr.append(mfvsrl.data)

                except MeteoForecastValues.DoesNotExist:
                    # no value associated
                    # Create new value

                    varsrl = MeteoForecValSrl(data=_d)

                    if varsrl.is_valid():
                        varsrl.save()

                        srl_attr.append(varsrl.data)

                except MeteoForecastValues.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "I04",
                        "message" : f"Meteorological Forecast has more than one value for one variable."
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status:
                    break

        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
            
            srl = MeteoForecSrl(mforec, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                if len(srl_attr):
                    response["vars"] = srl_attr

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Meteorological Forecast was updated."
                }, status.HTTP_200_OK

            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/forecast/{str(fid)}/',
            'service'  : 'manage-meteo-forec',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, fid, format=None):
        """
        Delete a Single Meteorological Forecast
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None

        qp = request.query_params
        
        try:
            mforec = MeteoForecast.objects.get(pk=fid)
        except MeteoForecast.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Forecast doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            mforec.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Meteorological Forecast deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/forecast/{str(fid)}/',
            'service'  : 'manage-meteo-forec',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        return rr  

