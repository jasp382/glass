"""
SDI related Views
"""

import datetime as dt
import pytz
import requests as rqsts

# REST Framework Dependencies
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework          import permissions
from rest_framework.parsers  import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc

from logs.srl import LogsSDISrl

from glass.firecons.gsrv import con_gsrv


################################################################################
# ########################### GeoServer - Layers ############################ #
################################################################################

class GeoServerLayers(APIView):
    """
    List/Create new Layer
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, format=None):
        """
        Method GET - Retrieve a list with all existing Geoserver layers
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:'
            f'{G["PORT"]}/geoserver/rest/layers'
        )

        try:
            r = rqsts.get(
                url, headers={'Accept': 'application/json'},
                auth=(G['USER'], G['PASSWORD'])
            )

            if r.status_code == 200:
                rsp = [] if r.json()['layers'] == '' else \
                    r.json()['layers']['layer']
            
                response, sc = {
                    "status" : {"code" : "S20", "message" : "Data successfully returned"},
                    "data"   : rsp
                }, status.HTTP_200_OK
            
            else:
                response, sc = {
                    "status" : {"code" : "GS2", "message" : "Something went wrong!"},
                    "data"   : r.content
                }, status.HTTP_404_NOT_FOUND

        except:
            response, sc = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST

        fresp = Response(response, status=sc)

        li = LogsSDISrl(data={
            'url'      : 'geosrv/layers/',
            'service'  : 'geoserver-layers',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    def post(self, request):
        """
        Method POST - Create new layer
        ---
        """

        from glass.wg.gsrv.lyr import addlyr, pub_rst_lyr
        from firerest.utils   import check_rqst_param

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Check parameters
        d, p = request.data, ['source', 'workspace', 'store', "store_type"]
        
        _status, http = check_rqst_param(p, d)
        
        if not _status:
            epsg = 3763 if not "epsg" in d else d["epsg"]

            # Create Geoserver Layer
            _type = 'raster' if d["store_type"] != 'psql' else 'psql'

            if _type == 'psql':
                is_r, r = addlyr(
                    d["source"], d['workspace'], d['store'],
                    epsg, 4326
                )
            
            else:
                is_r, r = pub_rst_lyr(
                    d["source"], d["store"], d["workspace"],
                    epsg
                )

            if is_r:
                txt = r.content.decode('utf-8')
                if r.status_code == 201:                    
                    _status, http = {
                        "code"    : "G21",
                        "message" : "New GeoServer layer was created"
                    }, status.HTTP_201_CREATED
                        
                elif r.status_code == 404:
                    # Workspace or store doesn't exist
                    _status, http = {
                        "code"    : "GS2",
                        "message" : txt
                    }, status.HTTP_404_NOT_FOUND
                        
                elif r.status_code == 400:
                    _status, http = {
                        "code"    : "GS2",
                        "message" : f"Table {d['table']} doesn't exist in db"
                    }, status.HTTP_400_BAD_REQUEST
                
                elif r.status_code == 500:
                    _status, http = {
                        "code"    : "GS2",
                        "message" : str(r.content)
                    }, status.HTTP_400_BAD_REQUEST
                
                else:
                    _status, http = {
                        "code"    : "GS2",
                        "message" : "Unknown error"
                    }, status.HTTP_400_BAD_REQUEST

            else:
                _status, http = {
                    "code"    : "GS1",
                    "message" : "Can't connect to GeoServer"
                }, status.HTTP_400_BAD_REQUEST
        
        response = {"status" : _status}
        
        resp = Response(response, status=http)

        log = LogsSDISrl(data={
            'url'      : 'geosrv/layers/',
            'service'  : 'geoserver-layers',
            'http'     : resp.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'method'   : request.method,
            'cuser'    : request.user.pk
        })

        if log.is_valid(): log.save()

        return resp


class GeoServerLayer(APIView):
    """
    Get, edit, delete GeoServer Layer
    """

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

        G = con_gsrv()
        
        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:"
            f"{G['PORT']}/geoserver/rest/layers/{lyr}"
        )
        
        try:
            rqs = rqsts.get(
                url, headers={'Accept' : 'application/json'},
                auth=(G["USER"], G["PASSWORD"])
            )
            
            if rqs.status_code == 200:
                response, http = {
                    "status" : {"code" : "S20", "message" : "Data successfully returned"},
                    "data"   : rqs.json()['layer']
                }, status.HTTP_200_OK
            else:
                response, http = {
                    "status" : {"code": "GS2", "message" : "Something went wrong!"},
                    "data"   : rqs.content
                }, status.HTTP_404_NOT_FOUND
        
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/layer/{lyr}/',
            'service'  : 'geoserver-layer',
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
    
    def put(self, request, lyr):
        """
        Assign style to layer
        """

        import json as js
        from firerest.utils import check_rqst_param

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
            f"geoserver/rest/layers/{lyr}/styles"
        )

        d, p = request.data, ["style"]

        _status, http = check_rqst_param(p, list(d.keys()))

        if not _status:
            try:
                _d = {'style' : {'name': d["style"]}}
                r = rqsts.post(
                    url, js.dumps(_d),
                    headers={'content-type': 'application/json'},
                    auth=(G["USER"], G["PASSWORD"])
                )

                if r.status_code == 201:
                    _status, http = {
                        "code"    : "G22",
                        "message" : "Layer style was updated"
                    }, status.HTTP_201_CREATED
                
                else:
                    _status, http = {
                        "code"    : "GS2",
                        "message" : str(r.content)
                    }, status.HTTP_400_BAD_REQUEST
            
            except:
                _status, http = {
                    "code"    : "GS1",
                    "message" : "Can't connect to GeoServer"
                }, status.HTTP_400_BAD_REQUEST
            
            response = {"status" : _status}
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/layer/{lyr}/',
            'service'  : 'geoserver-layer',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return rr

    def delete(self, request, lyr):
        """
        Method DELETE - Delete a specific layer
        ---
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        G = con_gsrv()
        
        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
            f"geoserver/rest/layers/{lyr}"
        )
        
        try:
            r = rqsts.delete(url, auth=(G["USER"], G["PASSWORD"]))
            
            if r.status_code == 200:
                response, http = {"status" : {
                    "code"    : "G23",
                    "message" : "GeoServer layer was deleted"
                }}, status.HTTP_200_OK
                
            else:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : "This layer doesn't exist"
                }}, status.HTTP_404_NOT_FOUND
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/layer/{lyr}/',
            'service'  : 'geoserver-layer',
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
