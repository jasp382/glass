"""
CAOP related views
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

from georef.models import Nutsii, Nutsiii, Concelhos, Freguesias, IneBgri
from georef.srl import NutsiiSrl, NutsSrl, ConcelhosSrl, BgriSrl

from logs.srl import LogsGeoRefSrl


class ManNutsII(APIView):
    """
    Manage NUT's II data
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Return All NUT-2
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        units = Nutsii.objects.all()
        srl   = NutsiiSrl(units, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK
    
        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/nut-ii/',
            'service'  : 'manage-nut-ii',
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
        Method POST - Add new NUT II
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["code", "name", "geom", "epsg"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

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
        
        # Add NUT II
        if not _status:
            srl = NutsiiSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "NUT II created"
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
            'url'      : 'georef/nut-ii/',
            'service'  : 'manage-nut-ii',
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
        Delete all NUT's II
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Delete cells
        NutsiiSrl.objects.all().delete()

        resp = {"status" : {
            "code"    : "S24",
            "message" : "All nut's were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/nut-ii/',
            'service'  : 'manage-nut-ii',
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


class ManNutII(APIView):
    """
    Manage one NUT II
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, nutid):
        """
        Method GET - Retrieve data of one NUT II
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            nut = Nutsii.objects.get(code=nutid)
        
        except Nutsii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT II doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = NutsiiSrl(nut)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : response}
        
        rr = Response(response, status=http)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-ii/{str(nutid)}/',
            'service'  : 'manage-one-nutii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def put(self, request, nutid):
        """
        Method PUT - Update NUT II
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["code", "geom", "name"]

        try:
            nut = Nutsii.objects.get(code=nutid)
            srl = NutsiiSrl(nut)
            nutd = srl.data
        except Nutsii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT II doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        warns = []
        if not _status:
            for p in rp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = nutd[p]

                    warns.append('geom not updated - epsg code is missing')

                    continue

                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj = None if d["epsg"] == 3763 else 3763
                    )

                    if not d[p]:
                        d[p] = nutd[p]

                        warns.append('geom not updated - geometry is missing')

                    continue

                if p not in d:
                    d[p] = nutd[p]
            
            srl = NutsiiSrl(nut, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "NUT II was updated.",
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
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-ii/{str(nutid)}/',
            'service'  : 'manage-one-nutii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def delete(self, request, nutid):
        """
        Method DELETE - Delete a specific NUT II
        ------
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            n = Nutsii.objects.get(code=nutid)
        
        except Nutsii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT II doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            n.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "NUT II deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-ii/{str(nutid)}/',
            'service'  : 'manage-one-nutii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr


class ManNutsIII(APIView):
    """
    Manage NUT's III data
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Return All NUT-III
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        units = Nutsiii.objects.all()
        srl   = NutsSrl(units, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK
    
        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/nut-iii/',
            'service'  : 'manage-nut-iii',
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
        Method POST - Add new NUT III
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["code", "name", "geom", "epsg", "nutii"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # Get NUT II
        if not _status:
            try:
                nutii = Nutsii.objects.get(code=rd["nutii"])
                rd["nutii"] = nutii.fid
            
            except Nutsii.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"NUT II {rd['nutii']} doesn't exist."
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
        
        # Add NUT III
        if not _status:
            srl = NutsSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "NUT III created"
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
            'url'      : 'georef/nut-iii/',
            'service'  : 'manage-nut-iii',
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
        Delete all NUT's II
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Delete cells
        NutsSrl.objects.all().delete()

        resp = {"status" : {
            "code"    : "S24",
            "message" : "All nut's were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/nut-iii/',
            'service'  : 'manage-nut-iii',
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


class ManNutIII(APIView):
    """
    Manage NUT III
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, nutid):
        """
        Method GET - Retrieve data of one NUT III
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            nut = Nutsiii.objects.get(code=nutid)
        
        except Nutsiii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT III doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = NutsSrl(nut)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-iii/{str(nutid)}/',
            'service'  : 'manage-one-nutiii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def put(self, request, nutid):
        """
        Method PUT - Update NUT III
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["code", "geom", "name", "nutii"]

        try:
            nut = Nutsiii.objects.get(code=nutid)
            srl = NutsSrl(nut)
            nutd = srl.data
        
        except Nutsiii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT III doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        warns = []
        if not _status:
            for p in rp:
                if p == 'nutii' and p in d:
                    try:
                        nutii = Nutsii.objects.get(code=d["nutii"])
                        d[p] = nutii.fid
                        continue
            
                    except Nutsii.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : f"NUT II {d['nutii']} doesn't exist."
                        }, status.HTTP_404_NOT_FOUND

                        break
                
                if p == 'geom' and 'epsg' not in d:
                    d[p] = nutd[p]

                    warns.append('geom not updated - epsg code is missing')

                    continue

                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj = None if d["epsg"] == 3763 else 3763
                    )

                    if not d[p]:
                        d[p] = nutd[p]

                        warns.append('geom not updated - geometry is missing')

                    continue

                if p not in d:
                    d[p] = nutd[p]
            
            srl = NutsSrl(nut, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "NUT III was updated.",
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
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-iii/{str(nutid)}/',
            'service'  : 'manage-one-nutiii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def delete(self, request, nutid):
        """
        Method DELETE - Delete a specific NUT III
        ------
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            n = Nutsiii.objects.get(code=nutid)
        
        except Nutsiii.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "NUT III doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            n.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "NUT III deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        ls = LogsGeoRefSrl(data={
            'url'      : f'georef/nut-iii/{str(nutid)}/',
            'service'  : 'manage-one-nutiii',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr


class ManConcelhos(APIView):
    """
    Manage Concelhos data
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Return All CONCELHOS
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        units = Concelhos.objects.all()
        srl   = ConcelhosSrl(units, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK
    
        fr = Response(r, status=h)

        # Write Logs
        ls = LogsGeoRefSrl(data={
            'url'      : 'georef/concelhos/',
            'service'  : 'manage-concelhos',
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
        Method POST - Add new Concelho
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["code", "name", "geom", "epsg", "nutiii"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # Get NUT II
        if not _status:
            try:
                nut = Nutsiii.objects.get(code=rd["nutiii"])
                rd["nutiii"] = nut.fid
            
            except Nutsiii.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"NUT III {rd['nutiii']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            # Sanitize geometry
            rd["geom"] = polygon_to_multipolygon(rd["geom"])

            if not rd["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
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
        
        # Add Concelho
        if not _status:
            srl = ConcelhosSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Concelho created"
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
            'url'      : 'georef/concelhos/',
            'service'  : 'manage-concelhos',
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
        Concelhos.objects.all().delete()

        resp = {"status" : {
            "code"    : "S24",
            "message" : "All concelhos were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/concelhos/',
            'service'  : 'manage-concelhos',
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


class ManBGRI(APIView):
    """
    Manage BGRI Units
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Return Statistic units
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        units = IneBgri.objects.all()
        srl   = BgriSrl(units, many=True)

        r, h = {
            "status" : {"code": code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        fr = Response(r, status=h)

        # Write logs
        logsrl = LogsGeoRefSrl(data={
            'url'      : 'georef/bgri/',
            'service'  : 'manage-bgri',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return fr

    def post(self, request):
        """
        Method POST - Add new BGRI Unit
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, rd = ["code", "lugid", "lugname", "geom", "epsg", "freg"], request.data

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # Get freguesia
        if not _status:
            try:
                freg = Freguesias.objects.get(code=rd["freg"])
                rd["freg"] = freg.id
            
            except Freguesias.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Freguesia {rd['freg']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
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
        
        # Add new unit
        if not _status:
            srl = BgriSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"] = {
                    "code"    : "S21",
                    "message" : "BGRI unit created"
                }
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : srl.errors
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        # Response
        rr = Response(response, status=http)

        # Write logs
        logi = LogsGeoRefSrl(data={
            'url'      : 'georef/bgri/',
            'service'  : 'manage-bgri',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(rd[k])}" for k in rd if k != 'geom'
            ]),
            'cuser'    : request.user.pk
        })

        if logi.is_valid(): logi.save()

        return rr
    

    def delete(self, request):
        """
        Delete all BGRI
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Delete units
        IneBgri.objects.all().delete()

        resp = {"status" : {
            "code"    : "I01",
            "message" : "All units were deleted"
        }}

        rr = Response(resp, status=status.HTTP_200_OK)

        # Write logs
        li = LogsGeoRefSrl(data={
            'url'      : 'georef/bgri/',
            'service'  : 'manage-bgri',
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

