"""
Meteorological Observation
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

from firerest.utils import check_rqst_param
from firerest.permcls import IsFireloc
from authapi.utils import id_usertype

from meteo.models import MeteoObservation, MeteoVariables
from meteo.models import MeteoStation,MeteoObservationValues 
from meteo.srl import MeteoObSrl, MeteoObsValSrl

from logs.srl import LogsMeteoSrl


class ManMeteoObservations(APIView):
    """
    Manage Meteorological Observations
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        List Meteorological Observation
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        mvar = MeteoObservation.objects.all()
        srl = MeteoObSrl(mvar, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/obs/',
            'service'  : 'manage-meteo-observations',
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
        Add new Meteorological Observation
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d = request.data

        pp = ["date", "station", "timezone"]

        _status, http = check_rqst_param(pp, list(d.keys()))

        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Check if date values are valid
            try:
                tt = dt.datetime.strptime(d["date"], '%Y-%m-%d %H:%M:%S')
                _tz = pytz.timezone(d["timezone"])

                d["date"] = _tz.localize(tt)
            
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" :  "Date has not the right format"
                }, status.HTTP_400_BAD_REQUEST

        # Get observation variables
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
        
        # Check if we have variables
        if not _status and not len(_vars):
            _status, http = {
                "code"    : "E01",
                "message" : "No variables data in the request"
            }, status.HTTP_400_BAD_REQUEST

        # Get station
        if not _status:
            try:
                sobj = MeteoStation.objects.get(idapi=d["station"])
                d["station"] = sobj.id
            except MeteoStation.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Meteo Station doesn't exist."
                }, status.HTTP_404_NOT_FOUND      
        
        
        if not _status:
            srl = MeteoObSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                vdata = [{
                    'obsid' : srl.data['id'],
                    'varid' : v.id,
                    'value' : round(float(d[v.slug]), 5)
                } for v in _vars]

                srlv = MeteoObsValSrl(data=vdata, many=True)

                if srlv.is_valid():
                    srlv.save()
        
                response = srl.data

                response["vars"] = srlv.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Meteorological Observation created."
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
            'url'      : 'meteo/obs/',
            'service'  : 'manage-meteo-observations',
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
        Delete all Meteorological Observations
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
            MeteoObservation.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Meteorological Observations deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/obs/',
            'service'  : 'manage-meteo-observations',
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
    
class ManMeteoObservation(APIView):
    """
    Manage a Single Meteorological Observation
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, obsid):
        """
        Get a Single Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None

        try:
            mobs = MeteoObservation.objects.get(pk=obsid)
        except MeteoObservation.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Observation doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MeteoObSrl(mobs)

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
            'url'      : f'meteo/obs/{obsid}/',
            'service'  : 'manage-meteo-observation',
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
    
    def put(self, request, obsid):
        """
        Update a Single Meteorological Observation
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["date", "station"]

        extattr = [k for k in d if k not in rp]

        tzs = list(pytz.all_timezones)

        if d["timezone"] not in tzs:
            _status, http = {
                "code"    : "E08",
                "message" : "timezone is invalid"
            }, status.HTTP_400_BAD_REQUEST

        if not _status:            
            try:
                mobs = MeteoObservation.objects.get(pk=obsid)
                srlo = MeteoObSrl(mobs)
                srldata = srlo.data

            except MeteoObservation.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Observation doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        # Get variables
        vars = []
        if not _status and len(extattr):
            # Get observation variables
            for var in extattr:
                try:
                    varobj = MeteoVariables.objects.get(slug=var)
                    vars.append(varobj)
                
                except MeteoVariables.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Meteorological Variable {var} doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break
        
        # Update variables values
        srl_attr = []
        if not _status and len(vars):
            for var in vars:
                dv = {
                    'varid' : var.id,
                    'obsid' : mobs.id,
                    'value' : round(float(d[var.slug]), 5)  
                }

                try: 
                    mov = MeteoObservationValues.objects.get(obsid=obsid, varid=var.id)
                    movsrl = MeteoObsValSrl(mov, data=dv)

                    if movsrl.is_valid():
                        movsrl.save()

                        srl_attr.append(movsrl.data)

                except MeteoObservationValues.DoesNotExist:
                    # no value associated
                    # Create new value
                
                    varsrl = MeteoObsValSrl(data=dv)

                    if varsrl.is_valid():
                        varsrl.save()

                        srl_attr.append(varsrl.data)

                except MeteoObservationValues.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "I04",
                        "message" : f"Meteorological Observation has more than one value for one variable."
                    }, status.HTTP_400_BAD_REQUEST

                if _status: break
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
     
            srl = MeteoObSrl(mobs, data=d)

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
            'url'      : f'meteo/obs/{obsid}/',
            'service'  : 'manage-meteo-observation',
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
    
    def delete(self, request, obsid, format=None):
        """
        Delete a Single Meteorological Observation
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None

        qp = request.query_params
        
        try:
            mobs = MeteoObservation.objects.get(pk=obsid)
        except MeteoObservation.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Observation doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            mobs.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Meteorological Observation deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/obs/{str(obsid)}/',
            'service'  : 'manage-meteo-observation',
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

