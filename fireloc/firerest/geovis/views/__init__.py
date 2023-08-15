"""
Views to manage Geoportal Layers
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

from geovis.srl import LayerAttrSrl, MapLayersSrl
from geovis.models import MapLayerAttr, MapLayers

from logs.srl import LogsGeovisSrl



class ManGLayers(APIView):

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

        ctx = {
            "astree" : None if "astree" in qp and qp["astree"] == 'false' \
                else True
        }

        attrs = MapLayers.objects.filter(level=1) if ctx["astree"] == True else \
            MapLayers.objects.all()

        srl = MapLayersSrl(attrs, many=True, context=ctx)

        code, mess = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }
        
        rr = Response(response, status=status.HTTP_200_OK)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/geoportal-layers/',
            'service'  : 'manage-geoportal-layers',
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

        d, cuser = request.data, request.user
        ustype = id_usertype(cuser)

        # Expected request parameters
        # param as key; max_length as value
        rp = {
            "slug" : 15, "designation" : 250, "workspace": 20,
            "store" : 20, "gsrvlyr": 40, "style": 20
        }

        pp = ["slug", "designation", "level"]

        allpp = list(rp.keys()) + pp + ["rootid"]

        # Check if we have all parameters
        _status, http = check_rqst_param(pp, list(d.keys()))

        # Check user type
        if not _status and ustype != 'superuser' and ustype != 'fireloc':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST

        # Check parameters length
        if not _status:
            for _rp in rp:
                if _rp not in d:
                    continue

                if len(d[_rp]) > rp[_rp]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {_rp} parameter is not valid "
                            f"(more than {str(rp[_rp])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Get Extra Attributes and check their length
        if not _status:
            eattr = [k for k in d if k not in allpp]

            for ea in eattr:
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
        
        if not _status:
            if "rootid" in d:
                try:
                    root = MapLayers.objects.get(slug=d["rootid"])

                    d["rootid"] = root.id
                except MapLayers.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Layer doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
            
            else:
                d["rootid"] = None
        
        if not _status:
            srl = MapLayersSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                if len(eattr):
                    attrd = [{
                        "slug" : a, "label": d[a],
                        "layerid": response['id']
                    } for a in eattr]

                    asrl = LayerAttrSrl(data=attrd, many=True)

                    if asrl.is_valid():
                        asrl.save()

                        response["lyrattr"] = asrl.data
                
                else:
                    response["lyrattr"] = None

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
            'url'      : 'geovis/geoportal-layers/',
            'service'  : 'manage-geoportal-layers',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : ";".join([f'{k}={str(d[k])}' for k in d]),
            'cuser'    : cuser.pk
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
            MapLayers.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "All layers were deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/geoportal-layers/',
            'service'  : 'manage-geoportal-layers',
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


class ManGLayer(APIView):

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
            lyri = MapLayers.objects.get(slug=lyr)
        
        except MapLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MapLayersSrl(lyri)

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
            'url'      : f'geovis/geoportal-layer/{lyr}/',
            'service'  : 'manage-geoportal-layer',
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

        rp = {
            "slug" : 15, "designation" : 50, "workspace": 20,
            "store" : 20, "gsrvlyr": 20, "style": 20
        }

        rd, pp = request.data, list(rp.keys()) + ['level', 'rootid']

        try:
            i = MapLayers.objects.get(slug=lyr)
            isrl = MapLayersSrl(i)
            lyr_ = isrl.data
        
        except MapLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Check parameters length
        if not _status:
            for _rp in rp:
                if _rp in rd and len(rd[_rp]) > rp[_rp]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {_rp} parameter is not valid "
                            f"(more than {str(rp[_rp])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break

        # Get Extra Attributes and check their length
        if not _status:
            eattr = [k for k in rd if k not in pp]

            for ea in eattr:
                if len(ea) > 15:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Slug {ea} is not valid "
                            "(more than 15 chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if len(rd[ea]) > 20:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Label {rd[ea]} is not valid "
                            "(more than 20 chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        if not _status:
            # Check if we need to delete all attributes first
            _replace = False if "replace" not in rd else rd["replace"] if \
                rd["replace"] == True or rd["replace"] == False else False

            # Delete if necessary
            if _replace:
                MapLayerAttr.objects.filter(layerid=lyr_['id']).delete()
            
            # Add to request data unpresent table fields
            for p in pp:
                if p not in rd:
                    rd[p] = lyr_[p]
            
            # Check which layer attributes are new and not
            ea_add = []
            ea_upd = []

            for ea in eattr:
                ad = {
                    "slug" : ea, "label" : rd[ea],
                    "layerid" : lyr_["id"]
                }

                try:
                    attr = MapLayerAttr.objects.get(slug=ea, layerid=lyr_['id'])

                    ea_upd.append({"obj" : attr, "data" : ad})
                
                except MapLayerAttr.DoesNotExist:
                    ea_add.append(ad)
            
            # Update MapLayer
            srl = MapLayersSrl(i, data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                if len(ea_add):
                    asrl = LayerAttrSrl(data=ea_add, many=True)

                    asrl.save()

                    response["lyrattr"] = asrl.data
                
                if len(ea_upd):
                    for ea in ea_upd:
                        usrl = LayerAttrSrl(ea["obj"], data=ea["data"])

                        usrl.save()

                        if "lyrattr" not in response:
                            response["lyrattr"] = [usrl.data]
                        else:
                            response["lyrattr"].append(usrl.data)
                
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Layer updated"
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
            'url'      : f'geovis/geoportal-layer/{lyr}/',
            'service'  : 'manage-geoportal-layer',
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
            attr = MapLayers.objects.get(slug=lyr)
        except MapLayers.DoesNotExist:
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
            'url'      : f'geovis/geoportal-layer/{lyr}/',
            'service'  : 'manage-geoportal-layer',
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



class RetrieveGLayers(APIView):
    """
    Give some Layers to unregisted users
    """

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve layers available to unregisted users
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        qp = request.query_params

        ctx = {
            "astree" : None if "astree" in qp and qp["astree"] == 'false' \
                else True
        }

        attrs = MapLayers.objects.filter(level=1) if ctx["astree"] == True \
            else MapLayers.objects.all()
        srl   = MapLayersSrl(attrs, many=True, context=ctx)

        code, mess = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }
        
        rr = Response(response, status=status.HTTP_200_OK)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/glayers-uu/',
            'service'  : 'list-geolayers-uu',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : None
        })

        if li.is_valid(): li.save()
        
        return rr

