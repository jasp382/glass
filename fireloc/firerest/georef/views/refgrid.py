"""
Reference GRID
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
from firerest.utils import check_rqst_param
from authapi.utils import id_usertype

from georef.models import RefGrid
from georef.srl import RefGridSrl

from logs.srl import LogsGeoRefSrl

class ManRefGrid(APIView):
    """
    [GET] - List Reference GRID Cells
    [POST] - Create a new Cell
    [DELETE] - Delete all Cells
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Return all Cells of the Reference Grid
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        cells = RefGrid.objects.all()
        srl   = RefGridSrl(cells, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK
    
        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/ref-grid/',
            'service'  : 'manage-reference-grid',
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
        Method POST - Add new cell to the reference grid
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["cellid", "geom", "epsg"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

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
        
        # Add cell
        if not _status:
            srl = RefGridSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Reference Cell created"
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
            'url'      : 'georef/ref-grid/',
            'service'  : 'manage-reference-grid',
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
        Delete all cells
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
            # Delete cells
            RefGrid.objects.all().delete()

            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "All cells were deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/ref-grid/',
            'service'  : 'manage-reference-grid',
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

