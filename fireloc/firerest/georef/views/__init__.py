"""
Reference Geospatial Datasets
"""

import datetime as dt
import pytz

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import wkt_sanitize

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from authapi.utils    import id_usertype

from georef.models import ExtentGeometry
from georef.srl import ExtSrl

from logs.srl import LogsGeoRefSrl


class Extent(APIView):
    """
    Manage extent geometry
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Return geometry
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        qp = request.query_params

        rgeom = True if "rgeom" in qp and qp["rgeom"] == 'true' \
            else None

        code, msg = "S20", "Data successfully returned"

        ctx = {
            "epsg" : None if "epsg" not in qp else int(qp["epsg"])
        }

        ext = ExtentGeometry.objects.all()
        srl = ExtSrl(ext, many=True, context=ctx)

        response = {} if not len(srl.data) else srl.data[0]

        if "geom" in response and not rgeom:
            del response["geom"]
        else:
            response["geom"] = ext[0].geom.wkt
        
        http = status.HTTP_200_OK

        response["status"] = {"code": code, "message" : msg}
    
        fr = Response(response, status=http)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/map-extent/',
            'service'  : 'manage-map-extent',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return fr
    
    def post(self, request):
        """
        Add geometry
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["geom", "epsg"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        if not _status:
            ext = ExtentGeometry.objects.all()

            if len(ext):
                _status, http = {
                    "code"    : "Z01",
                    "message" : "Geometry already exists"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Sanitize geometry
            rd["geom"] = wkt_sanitize(
                rd["geom"],
                epsg=3763 if rd["epsg"] == 3763 else rd["epsg"],
                reprj=3763 if rd["epsg"] != 3763 else None,
                rgeos=True
            )

            if not rd["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        # Add Geometry
        if not _status:
            srl = ExtSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Reference Geometry created"
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : srl.errors
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/map-extent/',
            'service'  : 'manage-map-extent',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def delete(self, request):
        """
        Delete geometry
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete geometries
            ExtentGeometry.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "All geometries were deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/map-extent/',
            'service'  : 'manage-map-extent',
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

