"""
Views to Manage Vector Datasets categories
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from firerest.utils import check_rqst_param
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc
from authapi.utils import id_usertype

from geovec.models import VectorCat
from geovec.srl import VecCatSrl
from logs.srl import LogsVecSrl



class ManVecCats(APIView):
    """
    List, create and delete Vector Datasets Categories

    Methods:
    GET | POST | DELETE

    URL:
    /geovec/vector-cat/

    Access:
    Private - Admin is required (superuser or fireloc user)
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Get the raster types available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        # Check params
        d = request.query_params

        # Get context object
        cat = VectorCat.objects.all()
        srl = VecCatSrl(cat, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"   : srl.data
        }

        fr = Response(response, status=status.HTTP_200_OK)

        # Write LOGS
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-cats/',
            'service'  : 'manage-vector-cats',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : ";".join([f"{str(k)}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr

    def post(self, request):
        """
        Create a new vector category in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, pp = request.data, ["slug", "name", "description"]

        _status, http = check_rqst_param(pp, d)

        if not _status:
            # Add Raster Type
            srl = VecCatSrl(data=d)

            if srl.is_valid():           
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Vector category was received and stored"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : srl.errors
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fresp = Response(response, http)
        
        # Write logs
        logi = LogsVecSrl(data={
            'url'      : 'geovec/vector-cats/',
            'service'  : 'manage-vector-cats',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logi.is_valid(): logi.save()
        
        return fresp

    def delete(self, request):
        """
        Delete all raster types
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser, _status, http = request.user, None, None
        ustype = id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete raster types
            VectorCat.objects.all().delete()

            response, http = {"status": {
                "code"    : "S24",
                "message" : "Vector Categories deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-cats/',
            'service'  : 'manage-vector-cats',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()
        
        return rr


class ManVecCat(APIView):
    """
    Get, edit and delete a specific Vector Dataset Category

    URL:
    /geovec/vector-dataset/<str:slugid>/

    Access:
    Private - Admin is required (superuser or fireloc user)
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request, slug):
        """
        Get a specfic raster dataset available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get vector dataset cat
        try:
            rd = VectorCat.objects.get(slug=slug)

        except VectorCat.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Category does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get instance data
        if not _status:
            srl = VecCatSrl(rd, many=False)

            response = srl.data
        
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data successfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        # Get response
        fr = Response(response, status=http)

        # Write LOGS
        li = LogsVecSrl(data={
            'url'      : f'geovec/vector-cat/{slug}/',
            'service'  : 'manage-vector-cat',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return fr

    def put(self, request, slug):
        """
        Edit a specfic vector dataset available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        params = ["slug", "name", "description"]

        # Get request data
        d, _status, http = request.data, None, None

        # Get vector dataset
        try:
            rd   = VectorCat.objects.get(slug=slug)
            srlv = VecCatSrl(rd)
            vdd  = srlv.data

        except VectorCat.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Dataset Category does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check request data
        if not _status:
            for f in params:
                if f not in d:
                    d[f] = vdd[f]

        # Update instance
        if not _status:
            srl = VecCatSrl(rd, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data
            
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Vector Category Updated"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fresp = Response(response, status=http)
        
        li = LogsVecSrl(data={
            'url'      : f'geovec/vector-cat/{slug}/',
            'service'  : 'manage-vector-cat',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return fresp
    
    def delete(self, request, slug):
        """
        Method DELETE - Delete a specific vector dataset cat
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get vector dataset cat
        try:
            vd = VectorCat.objects.get(slug=slug)

        except VectorCat.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Dataset Category does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Delete vector dataset
        if not _status:
            vd.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Vector dataset category deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : f'geovec/vector-cat/{slug}/',
            'service'  : 'manage-vector-cat',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return rr

