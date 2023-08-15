"""
Manage Meteorological Stations
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

from meteo.models import MeteoStation
from meteo.srl import MeteoStatSrl

from logs.srl import LogsMeteoSrl


class ManMeteoStations(APIView):
    """
    Manage Meteorological Stations
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        List Meteorological Stations
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        mstat = MeteoStation.objects.all()
        srl = MeteoStatSrl(mstat, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/stations/',
            'service'  : 'manage-meteo-stations',
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
        Add new Meteorological Stations
        """

    
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d = request.data
    
        pp = ["idapi", "name", "geom", "epsg"]

        _status, http = check_rqst_param(pp, list(d.keys()))
        
        if not _status:
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
                    "message" : "EPSG is not in Coordinate Reference System."
                }, status.HTTP_404_NOT_FOUND

        if not _status:

            srl = MeteoStatSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Meteorological Station created."
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
            'url'      : 'meteo/stations/',
            'service'  : 'manage-meteo-stations',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr

    def delete(self, request, format=None):
        """
        Delete all Meteorological Stations
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
            MeteoStation.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Meteorological Stations deleted"
            }}, status.HTTP_200_OK

        response = _status
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/stations/',
            'service'  : 'manage-meteo-stations',
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

    
class ManMeteoStation(APIView):
    """
    Manage a Single Meteorological Station
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request, idapi, format=None):
        """
        Get a Single Meteorological Station
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            mstat = MeteoStation.objects.get(idapi=idapi)
        except MeteoStation.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Station doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MeteoStatSrl(mstat)

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
            'url'      : f'meteo/station/{str(idapi)}/',
            'service'  : 'manage-meteo-station',
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
    
    def put(self, request, idapi, format=None):
        """
        Update a Single Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["idapi", 'name', 'geom']

        try:
            mstat   = MeteoStation.objects.get(idapi=idapi)
            srls    = MeteoStatSrl(mstat)
            srldata = srls.data
        except MeteoStation.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Station doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
                    continue
                
                if p == "geom" and "epsg" in d:
                    d[p] = wkt_sanitize(
                        d[p],
                        epsg=d["epsg"] if d["epsg"] != 3763 else 3763,
                        reprj=3763 if d["epsg"] != 3763 else None,
                        rgeos=True
                    )
                
                elif p == "geom" and "epsg" not in d:
                    d[p] = srldata[p]
     
            srl = MeteoStatSrl(mstat, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Meteorological Station was updated."
                }, status.HTTP_200_OK
            
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
            'url'      : f'meteo/station/{str(idapi)}/',
            'service'  : 'manage-meteo-station',
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

    def delete(self, request, idapi, format=None):
        """
        Delete a Single Meteorological Station
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            attr = MeteoStation.objects.get(idapi=idapi)
        except MeteoStation.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Station doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Meteorological Station deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/station/{str(idapi)}/',
            'service'  : 'manage-meteo-station',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        return rr

