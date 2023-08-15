"""
Views to Manage Raster Datasets
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

from georst.models import RasterDatasets, RasterTypes
from georst.srl import RasterDatasetSrl, RasterTypeSrl
from logs.srl import LogsGeoRstSrl


class ManRstTypes(APIView):
    """
    List, create and delete Raster Datasets Types

    Methods:
    GET | POST | DELETE

    URL:
    /georst/raster-types/

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
        rstd = RasterTypes.objects.all()
        srl = RasterTypeSrl(rstd, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"   : srl.data
        }

        fr = Response(response, status=status.HTTP_200_OK)

        # Write LOGS
        li = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-types/',
            'service'  : 'manage-raster-types',
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
        Create a new raster type in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get request data
        d = request.data

        # Check if we have all data we need
        mparams = ["slug", "name", "description"]
        _status, http = check_rqst_param(mparams, d)

        if not _status:
            # Add Raster Type
            srl = RasterTypeSrl(data=d)
            if srl.is_valid():           
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Raster Type was received and stored"
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
        logi = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-types/',
            'service'  : 'manage-raster-types',
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
            RasterTypes.objects.all().delete()

            response, http = {"status": {
                "code"    : "S24",
                "message" : "Raster Types deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-types/',
            'service'  : 'manage-raster-types',
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


class ManRstType(APIView):
    """
    Get, edit and delete a specific Raster Type

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

        # Get raster type
        try:
            rd = RasterTypes.objects.get(slug=slug)

        except RasterTypes.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Type does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get instance data
        if not _status:
            srl = RasterTypeSrl(rd, many=False)

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
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-type/{slug}/',
            'service'  : 'manage-raster-type',
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
            rd   = RasterTypes.objects.get(slug=slug)
            srlv = RasterTypeSrl(rd)
            vdd  = srlv.data

        except RasterTypes.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Type does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check request data
        if not _status:
            for f in params:
                if f not in d:
                    d[f] = vdd[f]

        # Update instance
        if not _status:
            srl = RasterTypeSrl(rd, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data
            
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Raster Type Updated"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fresp = Response(response, status=http)
        
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-type/{slug}/',
            'service'  : 'manage-raster-type',
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
            vd = RasterTypes.objects.get(slug=slug)

        except RasterTypes.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Type does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Delete vector dataset
        if not _status:
            vd.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Raster Type deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-type/{slug}/',
            'service'  : 'manage-raster-type',
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


class ManRstDatasets(APIView):
    """
    List, create and delete Raster Datasets

    Methods:
    GET | POST | DELETE

    URL:
    /georst/raster-datasets/

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
        Get the raster datasets available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
       
        # Get all raster datasets
        rstd = RasterDatasets.objects.all()
        srl  = RasterDatasetSrl(rstd, many=True)
        
        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"    : srl.data
        }
        
        #All good
        fr = Response(response, status=status.HTTP_200_OK)

        # Write LOGS
        li = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-datasets/',
            'service'  : 'manage-raster-datasets',
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
        Create a new raster datasets in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get request data
        rqstd = request.data

        # Check if we have all data we need
        mparams = [
            "slug", "name", "description", "source",
            "idtype"
        ]
        _status, http = check_rqst_param(mparams, rqstd)

        # Get Raster Dataset type
        if not _status:
            try:
                rsttype = RasterTypes.objects.get(slug=rqstd["idtype"])
                rqstd["idtype"] = rsttype.id
            
            except RasterTypes.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Raster Type doesn't exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Add Raster dataset
        if not _status:
            if "refyear" not in rqstd or type(rqstd["refyear"]) != int:
                rqstd["refyear"] = None
            
            if "refprod" not in rqstd or type(rqstd["refprod"]) != int:
                rqstd["refprod"] = None
            
            srl = RasterDatasetSrl(data=rqstd)
            
            if srl.is_valid():
                srl.save()

                response = srl.data
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Raster dataset was received and stored"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)
        
        # Write logs
        logi = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-datasets/',
            'service'  : 'manage-raster-datasets',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(rqstd[k])}" for k in rqstd
            ]),
            'cuser'    : request.user.pk
        })

        if logi.is_valid(): logi.save()
        
        return fresp
    
    def delete(self, request):
        """
        Delete all raster datasets of the system
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
            # Delete raster types
            RasterDatasets.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Raster Datasets deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-datasets/',
            'service'  : 'manage-raster-datasets',
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
    
    
class ManRstDataset(APIView):
    """
    Get, edit and delete a specific Raster Dataset

    URL:
    /georst/raster-dataset/<str:slugid>/

    Access:
    Private - Admin is required (superuser or fireloc user)
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request, slugid):
        """
        Get a specfic raster dataset available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get raster dataset
        try:
            rd = RasterDatasets.objects.get(slug=slugid)

        except RasterDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get instance data
        if not _status:
            srl = RasterDatasetSrl(rd, many=False)

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
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-dataset/{slugid}/',
            'service'  : 'manage-raster-dataset',
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

    def put(self, request, slugid):
        """
        Edit a specfic raster dataset available in the system
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        params = ["slug", "name", "description", "source", "idtype"]

        # Get request data
        rqstd, _status, http = request.data, None, None

        # Get raster dataset
        try:
            rd   = RasterDatasets.objects.get(slug=slugid)
            srlr = RasterDatasetSrl(rd)
            rdd  = srlr.data

        except RasterDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check request data
        if not _status:
            for f in params:
                if f == 'idtype' and f in rqstd:
                    try:
                        rsttype = RasterTypes.objects.get(slug=rqstd["idtype"])
                        rqstd["idtype"] = rsttype.id

                        continue
            
                    except RasterTypes.DoesNotExist:
                        _status = {
                            "code"    : "I03",
                            "message" : "Raster Type doesn't exist"
                        }, status.HTTP_404_NOT_FOUND

                        break
                
                if f not in rqstd:
                    rqstd[f] = rdd[f]

        # Update instance
        if not _status:
            srl = RasterDatasetSrl(rd, data=rqstd)

            if srl.is_valid():
                srl.save()

                response = srl.data
            
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Raster Dataset Updated"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fresp = Response(response, status=http)
        
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-dataset/{slugid}/',
            'service'  : 'manage-raster-dataset',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rqstd[k])}" for k in rqstd]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return fresp
    
    def delete(self, request, slugid):
        """
        Method DELETE - Delete a specific raster dataset
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get raster dataset
        try:
            rd = RasterDatasets.objects.get(slug=slugid)

        except RasterDatasets.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Raster Dataset does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Delete raster dataset
        if not _status:
            rd.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Raster dataset deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-dataset/{slugid}/',
            'service'  : 'manage-raster-dataset',
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

