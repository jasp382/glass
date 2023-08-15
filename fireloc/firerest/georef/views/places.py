"""
Places management views
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

from georef.models import Places
from georef.srl import PlacesSrl

from logs.srl import LogsGeoRefSrl


class ManPlaces(APIView):
    """
    Manage places and their locations
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Return all Places
        -----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        places = Places.objects.all()
        srl    = PlacesSrl(places, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/places/',
            'service'  : 'manage-places',
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
        Method POST - Add new Place
        -------
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["lugid", "lugname", "geom", "source", "epsg"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        if not _status:
            # Sanitize geometry
            rd["geom"] = wkt_sanitize(
                rd["geom"],
                epsg=3763 if rd["epsg"] == 3763 else rd["epsg"],
                reprj=None if rd["epsg"] == 3763 else 3763,
                rgeos=True
            )

            if not rd["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        # Todo: get freguesia
        
        # Add Place
        if not _status:
            if "altname" not in rd:
                rd["altname"] = None
            
            srl = PlacesSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Place created"
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
            'url'      : 'georef/places/',
            'service'  : 'manage-places',
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
        Method DELETE - Delete all places
        -------
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Delete cells
        PlacesSrl.objects.all().delete()

        resp = {"status" : {
            "code"    : "S24",
            "message" : "All places were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/places/',
            'service'  : 'manage-places',
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


class ManPlace(APIView):
    """
    Manage one Place
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, fid):
        """
        Method GET - Retrieve data of a place
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            pnt = Places.objects.get(pk=fid)
        except Places.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Place doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = PlacesSrl(pnt)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write Logs
        logsrl = LogsGeoRefSrl(data={
            'url'      : f'georef/place/{str(fid)}/',
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
    
    def put(self, request, fid):
        """
        Method PUT - Update Place
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["lugid", "lugname", "altname", "geom", "source"]

        try:
            pnt = Places.objects.get(pk=fid)
            srl = PlacesSrl(pnt)
            pntd = srl.data
        
        except Places.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Place doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        warns = []
        if not _status:
            for p in rp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = pntd[p]

                    warns.append('geom not updated - epsg code is missing')

                    continue

                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj = None if d["epsg"] == 3763 else 3763
                    )

                    if not d[p]:
                        d[p] = pntd[p]

                        warns.append('geom not updated - geometry is missing')

                    continue

                if p not in d:
                    d[p] = pntd[p]
            
            srl = PlacesSrl(pnt, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "Place was updated.",
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
            'url'      : f'georef/place/{str(fid)}/',
            'service'  : 'manage-place',
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

    def delete(self, request, fid):
        """
        Method DELETE - Delete a specific place
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            p = Places.objects.get(pk=fid)
        except Places.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Place doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            p.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Place deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        logsrl = LogsGeoRefSrl(data={
            'url'      : f'georef/place/{str(fid)}/',
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
