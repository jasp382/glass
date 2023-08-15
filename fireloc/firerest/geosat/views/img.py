"""
Sentinel Related Views
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework          import permissions
from rest_framework.parsers  import JSONParser

from drf_yasg.utils import swagger_auto_schema
from drf_yasg       import openapi

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.settings import PRJ_EPSG
from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from authapi.utils import id_usertype

from geosat.models import SentinelTiles, SentinelImages
from geosat.srl import SentinelImgSrl

from glass.prj.obj import prj_ogrgeom
from glass.gobj import wkt_sanitize

from logs.srl import LogsGeosatSrl


class ManSentinelImgs(APIView):
    """
    Manage Sentinel Images in the System
    """
    
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    query_param1 = openapi.Parameter('interestarea', openapi.IN_QUERY, type=openapi.TYPE_STRING)
    
    @swagger_auto_schema(
        manual_parameters=[query_param1],
        responses={200: SentinelImgSrl}
    )
    def get(self, request):
        """
        Method GET - Retrieve a list with all Sentinel
        images available to download
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        imgs = SentinelImages.objects.all()
        srl  = SentinelImgSrl(imgs, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }

        fresp = Response(response, status=status.HTTP_200_OK)

        li = LogsGeosatSrl(data={
            'url'      : 'dset/sentinel-imgs/',
            'service'  : 'manage-sentinel-images',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    
    request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'title':                       openapi.Schema(type=openapi.TYPE_STRING),
        'link':                        openapi.Schema(type=openapi.TYPE_STRING),
        'summary':                     openapi.Schema(type=openapi.TYPE_STRING),
        'ondemand':                    openapi.Schema(type=openapi.TYPE_STRING),
        'beginposition':               openapi.Schema(type=openapi.TYPE_STRING),
        'endposition':                 openapi.Schema(type=openapi.TYPE_STRING),
        'ingestiondate':               openapi.Schema(type=openapi.TYPE_STRING),
        'generationdate':              openapi.Schema(type=openapi.TYPE_STRING),
        'orbitnumber':                 openapi.Schema(type=openapi.TYPE_INTEGER),
        'relativeorbitnumber':         openapi.Schema(type=openapi.TYPE_STRING),
        'vegetationpercentage':        openapi.Schema(type=openapi.TYPE_NUMBER),
        'notvegetatedpercentage':      openapi.Schema(type=openapi.TYPE_NUMBER),
        'waterpercentage':             openapi.Schema(type=openapi.TYPE_NUMBER),
        'unclassifiedpercentage':      openapi.Schema(type=openapi.TYPE_NUMBER),
        'mediumprobacloudspercentage': openapi.Schema(type=openapi.TYPE_NUMBER),
        'highprobacloudspercentage':   openapi.Schema(type=openapi.TYPE_NUMBER),
        'snowicepercentage':           openapi.Schema(type=openapi.TYPE_NUMBER),
        'cloudcoverpercentage':        openapi.Schema(type=openapi.TYPE_NUMBER),
        'illuminationazimuthangle':    openapi.Schema(type=openapi.TYPE_NUMBER),
        'illuminationzenithangle':     openapi.Schema(type=openapi.TYPE_NUMBER),
        'level1cpdiidentifier':        openapi.Schema(type=openapi.TYPE_STRING),
        'format':                      openapi.Schema(type=openapi.TYPE_STRING),
        'processingbaseline':          openapi.Schema(type=openapi.TYPE_STRING),
        'platformname':                openapi.Schema(type=openapi.TYPE_STRING),
        'filename':                    openapi.Schema(type=openapi.TYPE_STRING),
        'instrumentname':              openapi.Schema(type=openapi.TYPE_STRING),
        'instrumentshortname':         openapi.Schema(type=openapi.TYPE_STRING),
        'size':                        openapi.Schema(type=openapi.TYPE_STRING),
        's2datatakeid':                openapi.Schema(type=openapi.TYPE_STRING),
        'producttype':                 openapi.Schema(type=openapi.TYPE_STRING),
        'platformidentifier':          openapi.Schema(type=openapi.TYPE_STRING),
        'orbitdirection':              openapi.Schema(type=openapi.TYPE_STRING),
        'platformserialidentifier':    openapi.Schema(type=openapi.TYPE_STRING),
        'processinglevel':             openapi.Schema(type=openapi.TYPE_STRING),
        'identifier':                  openapi.Schema(type=openapi.TYPE_STRING),
        'datastripidentifier':         openapi.Schema(type=openapi.TYPE_STRING),
        'granuleidentifier':           openapi.Schema(type=openapi.TYPE_STRING),
        'uuid':                        openapi.Schema(type=openapi.TYPE_STRING),
        'geometry':                    openapi.Schema(type=openapi.TYPE_STRING),
        'cellid':                      openapi.Schema(type=openapi.TYPE_INTEGER),
        'imgiarea':                    openapi.Schema(type=openapi.TYPE_INTEGER),
        'epsg':                        openapi.Schema(type=openapi.TYPE_STRING),
    })
    
    @swagger_auto_schema(request_body=request_body, responses={201: SentinelImgSrl})
    def post(self, request):
        """
        Method POST - Add new Image to know that it is available for download
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, decimals, attrs = request.data, [
            "vegetationpercentage", "notvegetatedpercentage",
            "waterpercentage", "unclassifiedpercentage",
            "mediumprobacloudspercentage", "highprobacloudspercentage",
            "snowicepercentage", "cloudcoverpercentage",
            "illuminationazimuthangle", "illuminationzenithangle"
        ], [
            'title', 'link', 'summary',
            'ondemand', 'beginposition', 'endposition', 'ingestiondate',
            'generationdate', 'orbitnumber', 'relativeorbitnumber',
            'vegetationpercentage', 'notvegetatedpercentage',
            'waterpercentage', 'unclassifiedpercentage',
            'mediumprobacloudspercentage', 'highprobacloudspercentage',
            'snowicepercentage', 'cloudcoverpercentage',
            'level1cpdiidentifier', 'format', 'processingbaseline',
            'platformname', 'filename', 'instrumentname',
            'instrumentshortname', 'size', 's2datatakeid', 'producttype',
            'platformidentifier', 'orbitdirection',
            'processinglevel', 'identifier', 'datastripidentifier',
            'granuleidentifier', 'uuid', 'geometry', 'tileid',
            "epsg", "isdownload"
        ]

        _status, http = check_rqst_param(attrs, list(d.keys()))

        if not _status:
            try:
                tile = SentinelTiles.objects.get(slugid=d["tileid"])
                d["tileid"] = tile.id
            
            except SentinelTiles.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Sentinel tile doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            # Round decimals
            for f in decimals:
                if f in d:
                    d[f] = round(d[f], 3)
            
            # Project geometry if necessary
            if int(d["epsg"]) != PRJ_EPSG:
                d["geometry"] = prj_ogrgeom(
                    d["geometry"], int(d["epsg"]), PRJ_EPSG,
                    geomIsWkt=True, outIsWkt=True, api="shply"
                )
            
            d["geometry"] = wkt_sanitize(d["geometry"], epsg=PRJ_EPSG)

            if not d["geometry"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geometry key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
            
        if not _status:
            # Add image
            srl = SentinelImgSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Sentinel Image created"
                }, status.HTTP_201_CREATED
            
            else:
                errors = srl.errors

                if 'uuid' in errors and errors['uuid'][0] == \
                    'sentinel images with this uuid already exists.':

                    response = {"status" : {
                        "code"    : "I02",
                        "message" : "sentinel images with this uuid already exists"
                    }}
                
                else:
                    response = {"status" : {
                        "code"    : "Z01",
                        "message" : errors
                    }}

                http = status.HTTP_400_BAD_REQUEST
        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)
        
        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : 'dset/sentinel-imgs/',
            'service'  : 'manage-sentinel-images',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    def delete(self, request):
        """
        Delete Images entries
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
            SentinelImages.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "All Images deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : 'dset/sentinel-img/',
            'service'  : 'manage-sentinel-images',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return rr


class ManSentinelImg(APIView):
    """
    Manage one Sentinel Image
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, imgid):
        """
        Method GET - Retrieve attributes of a sentinel cell
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get Image
        try:
            img = SentinelImages.objects.get(uuid=imgid)
        
        except SentinelImages.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Image does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = SentinelImgSrl(img, many=False)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data successfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-img/{imgid}/',
            'service'  : 'manage-sentinel-image',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr

    def put(self, request, imgid):
        """
        Edit image properties
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, data = None, None, request.data

        attrs = {
            'title' : 'str', 'link' : 'str', 'summary' : 'str',
            'ondemand' : 'str', 'beginposition' : 'datetime',
            'endposition' : 'datetime', 'ingestiondate' : 'datetime',
            'generationdate' : 'datetime', 'orbitnumber' : 'int',
            'relativeorbitnumber' : 'int', 'vegetationpercentage' : 'float',
            'notvegetatedpercentage' : 'float',
            'waterpercentage' : 'float', 'unclassifiedpercentage' : 'float',
            'mediumprobacloudspercentage' : 'float',
            'highprobacloudspercentage' : 'float',
            'snowicepercentage' : 'float', 'cloudcoverpercentage' : 'float',
            'illuminationazimuthangle' : 'float',
            'illuminationzenithangle' : 'float',
            'level1cpdiidentifier' : 'str', 'format' : 'str',
            'processingbaseline' : 'str', 'platformname' : 'str',
            'filename' : 'str', 'instrumentname' : 'str',
            'instrumentshortname' : 'str', 'size' : 'str',
            's2datatakeid' : 'str', 'producttype' : 'str',
            'platformidentifier' : 'str', 'orbitdirection' : 'str',
            'platformserialidentifier' : 'str',
            'processinglevel' : 'str', 'identifier' : 'str',
            'datastripidentifier' : 'str', 'granuleidentifier' : 'str',
            'uuid' : 'str'
        }

        decimals = [
            "vegetationpercentage", "notvegetatedpercentage",
            "waterpercentage", "unclassifiedpercentage",
            "mediumprobacloudspercentage", "highprobacloudspercentage",
            "snowicepercentage", "cloudcoverpercentage",
            "illuminationazimuthangle", "illuminationzenithangle"
        ]

        # Get instance
        try:
            img = SentinelImages.objects.get(id=imgid)
            isrl = SentinelImgSrl(img)
            idd  = isrl.data
        
        except SentinelImages.DoesNotExist:
            _status, http = {
                "code" : "I01",
                "message" : "Sentinel Image does not exist"
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            for p in attrs:
                if p not in data:
                    data[p] = idd[p]

                else:
                    if p in decimals:
                        data[p] = round(data[p], 3)
                        continue
            
                    if "geometry" in data and "epsg" in data:
                        if int(data["epsg"]) != 3857:

                            data["geometry"] = prj_ogrgeom(
                                data["geometry"], int(data["epsg"]), 3857,
                                geomIsWkt=True, outIsWkt=True, api="shply"
                            )
                        
                        data["geometry"] = wkt_sanitize(data["geometry"], epsg=3857)

                        continue

                    if p == 'cellid':
                        try:
                            cell = SentinelTiles.objects.get(slug=data["cellid"])
                            data["cellid"] = cell.id

                            continue
                        
                        except SentinelTiles.DoesNotExist:
                            _status, http = {
                                "code"    : "I03",
                                "message" : "Tile doesn't exist"
                            }, status.HTTP_404_NOT_FOUND

                            break
        
        if not _status:
            # Update data
            srl = SentinelImgSrl(img, data=data)

            if srl.is_valid():
                srl.save()

                response, http = srl.data, status.HTTP_201_CREATED

                response["status"] = {
                    "code"    : "S22",
                    "message" : "Sentinel image was updated"
                }
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : srl.errors 
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-img/{str(imgid)}/',
            'service'  : 'manage-one-image',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(data[k])}" for k in data]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    def delete(self, request, imgid):
        """
        Method DELETE - Delete sentinel cell
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get Image
        try:
            img = SentinelImages.objects.get(uuid=imgid)
        
        except SentinelImages.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Image does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Delete
        if not _status:
            img.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Image deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-img/{imgid}/',
            'service'  : 'manage-sentinel-image',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr

