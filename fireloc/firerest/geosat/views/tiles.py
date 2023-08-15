"""
Sentinel Tiles Views
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
from firerest.utils import check_rqst_param
from authapi.utils import id_usertype

from geosat.models import SentinelTiles
from geosat.srl import SentinelTileSrl, StlTileReadSrl

from logs.srl import LogsGeosatSrl

from glass.prj.obj import prj_ogrgeom
from glass.gobj import wkt_sanitize


class ManSentinelTiles(APIView):
    """
    Manage Sentinel Tiles
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]
    
    @swagger_auto_schema(responses={200: SentinelTileSrl})
    def get(self, request):
        """
        Method GET - Retrieve a list with all Sentinel Cells
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        qp = request.query_params

        ctx = {
            "showgeom" : True if "showgeom" in qp and \
                qp["showgeom"] == "true" else None,
            "epsg" : None if "epsg" not in qp else int(qp["epsg"]),
            "lastimg" : None if "lastimg" not in qp else True \
                if qp["lastimg"] == 'true' else None
        }

        tiles = SentinelTiles.objects.all()
        srl   = StlTileReadSrl(tiles, many=True, context=ctx)

        response, http = {
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        r = Response(response, status=http)

        li = LogsGeosatSrl(data={
            'url'      : 'geosat/sentinel-tiles/',
            'service'  : 'manage-sentinel-tiles',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return r


    request_body = openapi.Schema(type=openapi.TYPE_OBJECT, properties={
        'slugid': openapi.Schema(type=openapi.TYPE_STRING),
        'geom':   openapi.Schema(type=openapi.TYPE_STRING),
        'epsg':   openapi.Schema(type=openapi.TYPE_STRING),
    })
    
    @swagger_auto_schema(request_body=request_body, responses={201: SentinelTileSrl})
    def post(self, request):
        """
        Method POST - Create new Sentinel Tile
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd, params = request.data, ["slugid", "geom", "epsg"]

        resp, http = check_rqst_param(params, list(rd.keys()))
        
        if not resp:
            # Project geometry if necessary
            if int(rd["epsg"]) != PRJ_EPSG:
                rd["geom"] = prj_ogrgeom(
                    rd["geom"], int(rd["epsg"]), PRJ_EPSG,
                    geomIsWkt=True, outIsWkt=True
                )
            
            rd["geom"] = wkt_sanitize(rd["geom"], epsg=PRJ_EPSG)

            if not rd["geom"]:
                resp, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        if not resp:
            srl = SentinelTileSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Sentinel Tile created"
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : srl.errors
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : resp}
        
        fr = Response(response, status=http)

        # Write Logs
        li = LogsGeosatSrl(data={
            'url'      : 'geosat/sentinel-tile/',
            'service'  : 'manage-sentinel-tile',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr

    def delete(self, request):
        """
        Method DELETE - Delete all cells
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
            # Delete geometries
            SentinelTiles.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "All Cells deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : 'geosat/sentinel-tiles/',
            'service'  : 'manage-sentinel-tiles',
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



class ManSentinelTile(APIView):
    """
    Manage Sentinel Reference GRID Cell
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, tileid):
        """
        Method GET - Retrieve attributes of a sentinel cell
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            tile = SentinelTiles.objects.get(slugid=tileid)
        
        except SentinelTiles.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Sentinel tiles doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = SentinelTileSrl(tile)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-tile/{tileid}/',
            'service'  : 'manage-tile',
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
    
    def put(self, request, tileid):
        """
        Method PUT - Update attributes of a sentinel cell
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["slug", "geom"]

        try:
            tile = SentinelTiles.objects.get(slug=tileid)
            srl  = SentinelTileSrl(tile)
            td   = srl.data
        
        except SentinelTiles.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Sentinel Tile doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        warns = []
        if not _status:
            for p in rp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = td[p]

                    warns.append('geom not updated - epsg code is missing')

                    continue

                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj = None if d["epsg"] == 3763 else 3763
                    )

                    if not d[p]:
                        d[p] = td[p]

                        warns.append('geom not updated - geometry is missing')

                    continue

                if p not in d:
                    d[p] = td[p]
            
            srl = SentinelTileSrl(tile, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "Tile was updated.",
                    "warnings" : warns
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
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-tile/{tileid}/',
            'service'  : 'manage-tile',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join(f"{k}={str(d[k])}" for k in d),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr
    
    def delete(self, request, tileid):
        """
        Method DELETE - Delete sentinel cell
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            p = SentinelTiles.objects.get(slug=tileid)
        
        except SentinelTiles.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Sentinel tile doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            p.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Tile deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeosatSrl(data={
            'url'      : f'dset/sentinel-tile/{tileid}/',
            'service'  : 'manage-tile',
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

