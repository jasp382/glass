"""
Views to Manage Vector Datasets
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

from geovec.models import VectorDatasets, VectorCat
from geovec.srl import VectorDsetSrl

from logs.srl import LogsVecSrl


class ManVecDsets(APIView):
    """
    Retrieve, create and delete Vector Datasets
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Retrieve all vector datasets available in the system
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get all vector datasets
        dsets = VectorDatasets.objects.all()
        srl   = VectorDsetSrl(dsets, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"    : srl.data
        }

        #All good
        fr = Response(response, status=status.HTTP_200_OK)

        # Write LOGS
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-datasets/',
            'service'  : 'manage-vector-datasets',
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
        Create a new vector dataset in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        gtypes = [
            'POINT', 'LINESTRING', 'POLYGON',
            'MULTIPOINT', 'MULTILINESTRING', 'MULTIPOLYGON'
        ]

        d, pp = request.data, [
            "slug", "name", "description", "source",
            "gtype", "catid"
        ]
        _status, http = check_rqst_param(pp, d)

        if not _status and d["gtype"] not in gtypes:
            _status, http = {
                "code"    : "UNK",
                "message" : "geomtype value is not valid"
            }, status.HTTP_400_BAD_REQUEST
        
        # Get Vector Dataset type
        if not _status:
            try:
                vcat = VectorCat.objects.get(slug=d["catid"])
                d["catid"] = vcat.id
            
            except VectorCat.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Vector Cateogry doesn't exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Add vector dataset
        if not _status:
            if "refyear" not in d or type(d["refyear"]) != int:
                d["refyear"] = None
            
            if "refprod" not in d or type(d["refprod"]) != int:
                d["refprod"] = None
            
            srl = VectorDsetSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Vector dataset was created"
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
            'url'      : 'geovec/vector-datasets/',
            'service'  : 'manage-vector-datasets',
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
            VectorDatasets.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Vector Datasets deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : 'geovec/vector-datasets/',
            'service'  : 'manage-vector-datasets',
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


class ManVecDset(APIView):
    """
    Get, edit and delete a specific Vector Dataset

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

        # Get raster dataset
        try:
            rd = VectorDatasets.objects.get(slug=slug)

        except VectorDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get instance data
        if not _status:
            srl = VectorDsetSrl(rd, many=False)

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
            'url'      : f'geovec/vector-dataset/{slug}/',
            'service'  : 'manage-vector-dataset',
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

        params = ["slug", "name", "description", "source", "gtype", "catid"]

        # Get request data
        d, _status, http = request.data, None, None

        # Get vector dataset
        try:
            rd   = VectorDatasets.objects.get(slug=slug)
            srlv = VectorDsetSrl(rd)
            vdd  = srlv.data

        except VectorDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check request data
        if not _status:
            for f in params:
                if f == 'catid' and f in d:
                    try:
                        vcat = VectorCat.objects.get(slug=d["catid"])
                        d["catid"] = vcat.id

                        continue
            
                    except VectorCat.DoesNotExist:
                        _status = {
                            "code"    : "I03",
                            "message" : "Vector Cateogry doesn't exist"
                        }, status.HTTP_404_NOT_FOUND

                        break
                
                if f not in d:
                    d[f] = vdd[f]

        # Update instance
        if not _status:
            srl = VectorDsetSrl(rd, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data
            
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Vector Dataset Updated"
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
            'url'      : f'geovec/vector-dataset/{slug}/',
            'service'  : 'manage-vector-dataset',
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
            vd = VectorDatasets.objects.get(slug=slug)

        except VectorDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Vector Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Delete vector dataset
        if not _status:
            vd.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Vector dataset deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsVecSrl(data={
            'url'      : f'geovec/vector-dataset/{slug}/',
            'service'  : 'manage-vector-dataset',
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

