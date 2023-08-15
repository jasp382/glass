"""
Views to manage Cluster Layers
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

from geovis.srl import ClusterLayersSrl
from geovis.models import ClusterLayers


from logs.srl import LogsGeovisSrl


class ManClusterLayers(APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve existing layers
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        qp = request.query_params

        if "del_lastlevel" in qp:
            cl = ClusterLayers.objects.all().order_by("-level")[1:]
        
        else:
            cl  = ClusterLayers.objects.all().order_by("level")

        srl = ClusterLayersSrl(cl, many=True)

        code, mess = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }
        
        rr = Response(response, status=status.HTTP_200_OK)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/cluster-layers/',
            'service'  : 'manage-cluster-layers',
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
        Method POST - Add new layer
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d = request.data

        # Expected request parameters
        # param as key; max_length as value
        rp = [
            "slug", "designation", "workspace", "store",
            "gsrvlyr", "eps", "minpts", "maxzoom", "minzoom",
            "level"
        ]
        mlen = {
            "slug" : 15, "designation" : 50, "workspace": 20,
            "store" : 20, "gsrvlyr": 40
        }

        # Check if we have all parameters
        _status, http = check_rqst_param(rp, list(d.keys()))

        # Check parameters length
        if not _status:
            for _rp in mlen:
                if len(str(d[_rp])) > mlen[_rp]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {_rp} parameter is not valid "
                            f"(more than {str(rp[_rp])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST

                if _status: break

        if not _status:
            srl = ClusterLayersSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Layer Created"
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
            'url'      : 'geovis/cluster-layers/',
            'service'  : 'manage-cluster-layers',
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
        Method DELETE - Delete all layers
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
            ClusterLayers.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "All layers were deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/cluster-layers/',
            'service'  : 'manage-cluster-layers',
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


class ManClusterLayer(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    
    parser_classes = [JSONParser]

    def get(self, request, lyr):
        """
        Method GET - Retrieve a specific layer
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            lyri = ClusterLayers.objects.get(slug=lyr)
        
        except ClusterLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = ClusterLayersSrl(lyri)

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
            'url'      : f'geovis/cluster-layer/{lyr}/',
            'service'  : 'manage-cluster-layer',
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

        _status, http, rd = None, None, request.data

        rp = [
            "slug", "designation", "workspace", "store",
            "gsrvlyr", "eps", "minpts", "maxzoom", "minzoom",
            "level"
        ]

        plen = {
            "slug" : 15, "designation" : 50, "workspace": 20,
            "store" : 20, "gsrvlyr": 40
        }

        try:
            cl   = ClusterLayers.objects.get(slug=lyr)
            isrl = ClusterLayersSrl(cl)
            lyr_ = isrl.data
        
        except ClusterLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Check parameters length
        if not _status:
            for _rp in plen:
                if _rp in rd and len(rd[_rp]) > plen[_rp]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {_rp} parameter is not valid "
                            f"(more than {str(rp[_rp])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        if not _status:
            # Add to request data unpresent table fields
            for p in rp:
                if p not in rd:
                    rd[p] = lyr_[p]

            # Update MapLayer
            srl = ClusterLayersSrl(cl, data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Layer updated"
                }, status.HTTP_201_CREATED

            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}    

        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/cluster-layer/{lyr}/',
            'service'  : 'manage-cluster-layer',
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
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = ClusterLayers.objects.get(slug=lyr)
        except ClusterLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Layer deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/cluster-layer/{lyr}/',
            'service'  : 'manage-cluster-layer',
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

