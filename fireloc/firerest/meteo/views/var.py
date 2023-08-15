"""
Meteorological Variables
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

from meteo.models import MeteoVariables, MeteoSource
from meteo.srl import MeteoVarSrl

from logs.srl import LogsMeteoSrl


class ManMeteoVars(APIView):
    """
    Manage Meteorological Variables
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        List Meteorological Variables
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        mvar = MeteoVariables.objects.all()
        srl = MeteoVarSrl(mvar, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/var/',
            'service'  : 'manage-meteo-variables',
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
        Add new Meteorological Variable
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d = request.data

        pp = [
            "slug", "name", "description",
            "unit", "source"
        ]

        _status, http = check_rqst_param(pp, list(d.keys()))

        if not _status:
            try:
                src = MeteoSource.objects.get(slug=d["source"])
                d["source"] = src.id
            
            except MeteoSource.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Source doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        if not _status:
            try:
                mv = MeteoVariables.objects.get(slug=d["slug"])
                _status, http = {
                    "code"    : "I03", 
                    "message" : f'Meteorological Variable {d["slug"]} already exist.'
                }, status.HTTP_400_BAD_REQUEST
            except:
                pass

        if not _status:
            srl = MeteoVarSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Meteorological Variable created."
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
            'url'      : 'meteo/var/',
            'service'  : 'manage-meteo-variables',
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
    
    def delete(self, request):
        """
        Delete all Meteorological Variables
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
            MeteoVariables.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Meteorological Variables deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : 'meteo/var/',
            'service'  : 'manage-meteo-variables',
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


class ManMeteoVar(APIView):
    """
    Manage a Single Meteorological Variable
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, slug):
        """
        Get a Single Meteorological Variable
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            mvar = MeteoVariables.objects.get(slug=slug)
        except MeteoVariables.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Variable doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MeteoVarSrl(mvar)

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
            'url'      : f'meteo/var/{str(slug)}/',
            'service'  : 'manage-meteo-variable',
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
        Update a Single Meteorological variable
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = [
            "slug", 'name', 'description', 
            "unit", "source"
        ]

        try:
            mvar = MeteoVariables.objects.get(slug=slug)
            srlv = MeteoVarSrl(mvar)
            srldata = srlv.data
        
        except MeteoVariables.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Variable doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        
        if not _status:
            for p in rp:
                if p == 'source' and p in d:
                    try:
                        src = MeteoSource.objects.get(slug=d["source"])
                        d[p] = src.id

                        continue
                    
                    except MeteoSource.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "Source doesn't exist."
                        }, status.HTTP_404_NOT_FOUND

                        break
                
                if p not in d:
                    d[p] = srldata[p]
        
        if not _status:     
            srl = MeteoVarSrl(mvar, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Meteorological variable was updated."
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
            'url'      : f'meteo/var/{str(slug)}/',
            'service'  : 'manage-meteo-variable',
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
        Delete a Single Meteorological Variable
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            attr = MeteoVariables.objects.get(slug=slug)
        except MeteoVarSrl.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Variable doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Meteorological variable deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsMeteoSrl(data={
            'url'      : f'meteo/var/{str(slug)}/',
            'service'  : 'manage-meteo-variable',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        return rr
    
