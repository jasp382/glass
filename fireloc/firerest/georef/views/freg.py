"""
CAOP Freguesias related views
"""

import datetime as dt
import pytz

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import polygon_to_multipolygon, wkt_sanitize

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param

from georef.models import Concelhos, Freguesias
from georef.srl import FregSrl, ReadFregSrl

from logs.srl import LogsGeoRefSrl


class ManFregs(APIView):
    """
    Manage Freguesias data
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Return All FREGUESIAS
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        d = request.query_params

        ctx = {
            "showgeom" : True if "showgeom" in d and \
                d["showgeom"] == "true" else None,
            "epsg" : None if "epsg" not in d else int(d["epsg"])
        }

        units = Freguesias.objects.all()
        srl   = ReadFregSrl(units, context=ctx, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK
    
        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/freguesias/',
            'service'  : 'manage-fregs',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : ';'.join([f"{k}={d[k]}" for k in d]),
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return fr
    
    def post(self, request):
        """
        Method POST - Add new Freguesia
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["code", "name", "geom", "epsg", "munid"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # Get Municipality
        if not _status:
            try:
                mun = Concelhos.objects.get(code=rd["munid"])
                rd["munid"] = mun.fid
            
            except Concelhos.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Concelho {rd['mun']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            # Sanitize geometry
            rd["geom"] = polygon_to_multipolygon(rd["geom"])

            if not rd["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : "Geometry is invalid"
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
        
        # Add Freguesia
        if not _status:
            srl = FregSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Freguesia created"
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
            'url'      : 'georef/freguesias/',
            'service'  : 'manage-fregs',
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
        Delete all Concelhos
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Delete cells
        Freguesias.objects.all().delete()

        resp = {"status" : {
            "code"    : "S24",
            "message" : "All freguesias were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/freguesias/',
            'service'  : 'manage-fregs',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : resp["status"]['code'],
            'message'  : resp["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr


class ManFreg(APIView):
    """
    Manage One Freguesia
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, code):
        """
        Method GET - Retrieve specific Freguesia
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            freg = Freguesias.objects.get(code=code)
        except Freguesias.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Freguesia doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = ReadFregSrl(freg)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : f'georef/freguesia/{code}/',
            'service'  : 'manage-freg',
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
    
    def put(self, request, code):
        """
        Method PUT - Update Freguesia
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        pp= ["code", "name", "geom", "munid"]

        try:
            freg  = Freguesias.objects.get(code=code)
            srl   = FregSrl(freg)
            fregd = srl.data
        except Freguesias.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Freguesia doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        warns = []
        if not _status:
            for p in pp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = fregd[p]

                    warns.append('geom not updated - epsg code is missing')
                
                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj = None if d["epsg"] == 3763 else 3763
                    )

                    if not d[p]:
                        d[p] = fregd[p]

                        warns.append('geom not updated - geometry is missing')

                    continue

                if p not in d:
                    d[p] = fregd[p]
            
            srl = FregSrl(freg, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "Freguesia was updated.",
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
        
        # Write Logs
        logsrl = LogsGeoRefSrl(data={
            'url'      : f'georef/freguesia/{code}/',
            'service'  : 'manage-freg',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={d[k]}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, code):
        """
        Method DELETE - Delete a specific freguesia
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            p = Freguesias.objects.get(code=code)
        except Freguesias.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Freguesia doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            p.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Freguesia deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        logsrl = LogsGeoRefSrl(data={
            'url'      : f'georef/freguesia/{code}/',
            'service'  : 'manage-place',
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

