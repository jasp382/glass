"""
Views to manage Vector Datasets Levels
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

from geovec.models import VectorDatasets, VectorLevels
from geovec.srl import VectorLevelsSrl

from logs.srl import LogsVecSrl


class ManVecLevels(APIView):
    """
    Retrieve, create and delete Vector Datasets Levels
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Retrieve all vector levels in the system
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get all vector datasets levels
        dsets = VectorLevels.objects.all()
        srl   = VectorLevelsSrl(dsets, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"   : srl.data
        }

        #All good
        fr = Response(response, status=status.HTTP_200_OK)

        # Write LOGS
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-levels/',
            'service'  : 'manage-vector-levels',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr

    def post(self, request):
        """
        Create a new vector level
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, pp = request.data, [
            "slug", "name", "description", "level",
            "dsetid"
        ]

        _status, http = check_rqst_param(pp, d)
        
        # Get Vector Dataset
        if not _status:
            try:
                v = VectorDatasets.objects.get(slug=d["dsetid"])
                d["dsetid"] = v.id
            
            except VectorDatasets.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Vector Dataset doesn't exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Add vector dataset level
        if not _status:
            srl = VectorLevelsSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Vector level was received and stored"
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
        logi = LogsVecSrl(data={
            'url'      : 'geovec/vector-levels/',
            'service'  : 'manage-vector-levels',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logi.is_valid(): logi.save()
        
        return rr
    
    def delete(self, request):
        """
        Delete all vector datasets of the system
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
            # Delete vector types
            VectorLevels.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Vector Levels deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-levels/',
            'service'  : 'manage-vector-levels',
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


class ManVecLevel(APIView):
    """
    Get, edit and delete a specific Vector Level

    URL:
    /geovec/vector-level/<str:slug>/

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

        # Get vector level
        try:
            rd = VectorLevels.objects.get(slug=slug)

        except VectorLevels.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Level does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get instance data
        if not _status:
            srl = VectorLevelsSrl(rd, many=False)

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
            'url'      : f'geovec/vector-level/{slug}/',
            'service'  : 'manage-vector-level',
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
        Edit a specfic vector level
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        params = ["slug", "name", "description", "level", "dsetid"]

        # Get request data
        d, _status, http = request.data, None, None

        # Get vector dataset
        try:
            rd   = VectorLevels.objects.get(slug=slug)
            srlv = VectorLevelsSrl(rd)
            vdd  = srlv.data

        except VectorLevels.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Level does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check request data
        if not _status:
            for f in params:
                if f == 'dsetid' and f in d:
                    try:
                        dset = VectorDatasets.objects.get(slug=d["dsetid"])
                        d["dsetid"] = dset.id

                        continue
            
                    except VectorDatasets.DoesNotExist:
                        _status = {
                            "code"    : "I03",
                            "message" : "Vector Dataset doesn't exist"
                        }, status.HTTP_404_NOT_FOUND

                        break
                
                if f not in d:
                    d[f] = vdd[f]

        # Update instance
        if not _status:
            srl = VectorLevelsSrl(rd, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data
            
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Vector Level Updated"
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
            'url'      : f'geovec/vector-level/{slug}/',
            'service'  : 'manage-vector-level',
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
        Method DELETE - Delete a specific vector dataset
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get vector dataset
        try:
            vd = VectorLevels.objects.get(slug=slug)

        except VectorLevels.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Level does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Delete vector level
        if not _status:
            vd.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Vector level deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : f'geovec/vector-level/{slug}/',
            'service'  : 'manage-vector-level',
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

