"""
Views to manage Contribution Layers
"""


import datetime as dt
import pytz

# Rest Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from authapi.utils    import id_usertype

from geovis.srl     import SCtbLyrSrl
from geovis.models  import SingleCtbLayers
from contrib.models import VolunteersContributions

from logs.srl import LogsGeovisSrl



class ManSingleCtbLayers(APIView):
    """
    Deal with geoserver services specific for
    each contribution
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all contributions services
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        lyr = SingleCtbLayers.objects.all()
        srl = SCtbLyrSrl(lyr, many=True)

        code, mess = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }

        rr = Response(response, status=status.HTTP_200_OK)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/single-ctb-layers/',
            'service'  : 'single-contribution-layers',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return rr

    def post(self, request):
        """
        Method POST - Add new contribution layer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d = request.data

        # Expected request parameters
        # param as key; max_length as value
        mlen = {
            "slug" : 15, "desig" : 100, "work": 20,
            "store" : 20, "layer": 40, "style": 20
        }

        pp = [
            "slug", "desig", "work", "store",
            "layer", "wms", "ctb"
        ]

        # Check if we have all parameters
        _status, http = check_rqst_param(pp, list(d.keys()))

        pp.append("style")

        if not _status:
            try:
                c = VolunteersContributions.objects.get(pk=d["ctb"])
                d["ctb"] = c.fid
            
            except VolunteersContributions.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Contribution doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        # Check parameters length
        if not _status:
            for p in mlen:
                if p in d and d[p] and len(d[p]) > mlen[p]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {p} parameter is not valid "
                            f"(more than {str(mlen[p])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Get Extra Attributes and check their length
        if not _status:
            eattr = [k for k in d if k not in pp]

            for ea in eattr:
                if not d[ea]: continue
                
                if len(ea) > 15:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Slug {ea} is not valid "
                            "(more than 15 chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if len(d[ea]) > 20:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Label {d[ea]} is not valid "
                            "(more than 20 chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Add data to the database
        if not _status:
            if "style" not in d:
                d["style"] = None
            
            srl = SCtbLyrSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Contribution Layer Created"
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/single-ctb-layers/',
            'service'  : 'single-contribution-layers',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : ";".join([f'{k}={str(d[k])}' for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr
    
    def delete(self, request):
        """
        Method DELETE - Delete all contribution layers
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Check user permissions
        cuser = request.user
        ustype = id_usertype(cuser)

        if ustype != 'superuser':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action"
            },  status.HTTP_403_FORBIDDEN

        # Delete data
        if not _status:
            SingleCtbLayers.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "All layers were deleted"
            }}, status.HTTP_200_OK
        
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/single-ctb-layers/',
            'service'  : 'single-contribution-layers',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return rr


class ManSingleCtbLayer(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    
    parser_classes = [JSONParser]

    def get(self, request, lyr):
        """
        Method GET - Retrieve a specific layer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            lyri = SingleCtbLayers.objects.get(slug=lyr)
        
        except SingleCtbLayers.DoesNotExist:
            _status, http = {"status" : {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }}, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = SCtbLyrSrl(lyri)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
                
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        # Write logs
        li = LogsGeovisSrl(data={
            'url'      : f'geovis/single-ctb-layer/{lyr}/',
            'service'  : 'single-contribution-layer',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return r
    
    def put(self, request, lyr):
        """
        Method PUT - Edit layer
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        rp, rd = {
            "slug" : 15, "design" : 100, "work": 20,
            "store" : 20, "layer": 40, "style": 20,
            "wms" : 0, "ctb" : 0
        }, request.data

        try:
            i    = SingleCtbLayers.objects.get(slug=lyr)
            isrl = SCtbLyrSrl(i)
            lyr_ = isrl.data
        
        except SingleCtbLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Check parameters length
        if not _status:
            for p in rp:
                if p not in rd:
                    rd[p] = lyr_[p]

                    continue
                
                if rp[p] and p in rd and len(rd[p]) > rp[p]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {p} parameter is not valid "
                            f"(more than {str(rp[p])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        if not _status:
            # Update MapLayer
            srl = SCtbLyrSrl(i, data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Layer updated"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
            
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/single-ctb-layer/{lyr}/',
            'service'  : 'single-contribution-layer',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={rd[k]}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr
    
    def delete(self, request, lyr):
        """
        Method DELETE - Delete layer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            lyr = SingleCtbLayers.objects.get(slug=lyr)
        
        except SingleCtbLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            lyr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Layer deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/single-ctb-layer/{lyr}/',
            'service'  : 'single-contribution-layer',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr

