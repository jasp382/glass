"""
Meteorological Source
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

from meteo.models import MeteoSource
from meteo.srl import MeteoSrcSrl

from logs.srl import LogsMeteoSrl


class ManMeteoSources(APIView):
    """
    Manage Meteorological Sources
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        List Meteorological Sources
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        msrc = MeteoSource.objects.all()
        srl = MeteoSrcSrl(msrc, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/src/',
            'service'  : 'manage-meteo-sources',
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
        Add new Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d = request.data

        pp = [
            "slug", "name", "description",
            "url", "token"
        ]

        _status, http = check_rqst_param(pp, list(d.keys()))
        
        if not _status:
            srl = MeteoSrcSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Meteorological Source created."
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
            'url'      : 'meteo/src/',
            'service'  : 'manage-meteo-sources',
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
        Delete all Meteorological Sources
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
            MeteoSource.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Meteorological Sources deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/src/',
            'service'  : 'manage-meteo-sources',
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


class ManMeteoSource(APIView):
    """
    Manage a Single Meteorological Source
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, slug, format=None):
        """
        Get a Single Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            msrc = MeteoSource.objects.get(slug=slug)
        except MeteoSource.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Source doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MeteoSrcSrl(msrc)

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
            'url'      : f'meteo/src/{str(slug)}/',
            'service'  : 'manage-meteo-source',
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
    
    def put(self, request, slug, format=None):
        """
        Update a Single Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = [
            "slug", 'name', 'description', 
            "url", "token"
        ]

        try:
            msrc = MeteoSource.objects.get(slug=slug)
            srl = MeteoSrcSrl(msrc)
            srldata = srl.data
        except MeteoSource.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Source doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
     
            srl = MeteoSrcSrl(msrc, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Meteorological Source was updated."
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
            'url'      : f'meteo/src/{str(slug)}/',
            'service'  : 'manage-meteo-source',
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
    
    def delete(self, request, slug, format=None):
        """
        Delete a Single Meteorological Source
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            attr = MeteoSource.objects.get(slug=slug)
        except MeteoSource.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Source doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Meteorological Source deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/src/{str(slug)}/',
            'service'  : 'manage-meteo-source',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        return rr
    
