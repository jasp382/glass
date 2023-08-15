"""
Manage Stores
"""

import datetime as dt
import requests as rqsts
import pytz
import os

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc

from logs.srl import LogsSDISrl

from glass.firecons.gsrv import con_gsrv

################################################################################
# ########################### GeoServer - Stores ############################# #
################################################################################

class GeoServerStores(APIView):
    """
    List/Create Stores inside workspace
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, ws):
        """
        Method GET - List Stores in GeoServer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
            f'geoserver/rest/workspaces/{ws}/datastores'
        )

        try:
            r = rqsts.get(
                url, headers={'Accept' : 'application/json'},
                auth=(G["USER"], G["PASSWORD"])
            )
            
            if r.status_code == 200:
                
                rsp = [] if r.json()['dataStores'] == '' else \
                    r.json()['dataStores']['dataStore']

                response, sc = {
                    "status" : {"code": "S20", "message" : "Data successfully returned"},
                    "data"   : rsp
                }, status.HTTP_200_OK
            
            else:
                response, sc = {"status" : {
                    "code" : "GS2",
                    "message": r.content
                }}, status.HTTP_404_NOT_FOUND
        
        except:
            response, sc = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        fresp = Response(response, status=sc)

        li = LogsSDISrl(data={
            'url'      : f'geosrv/{ws}/stores/',
            'service'  : 'geoserver-stores',
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
    
    def post(self, request, ws):
        """
        Method POST - Create new store
        ---
        """

        from glass.wg.gsrv.st import add_pgstore, add_rststore
        from firerest.utils  import check_rqst_param

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        rd, p = request.data, ['store', 'source', 'store_type']

        # Check if parameters are valid
        _status, http = check_rqst_param(p, rd)
        
        if not _status:
            add_store = add_rststore if rd["store_type"] != 'psql' \
                else add_pgstore
            
            src = rd["source"] if rd["store_type"] == 'psql' else \
                os.path.join(G[rd["store_type"]], rd["source"])
            
            # Create GeoServer Store
            is_r, r = add_store(src, ws, rd["store"])

            if is_r:
                # Check GeoSERVER response
                txt = r.content.decode('utf-8')

                rwrong = {"status" : {"code": "GSRV4", "message" : txt}}

                if r.status_code == 201:
                    response, http = {"status" : {
                        "code"    : "G21",
                        "message" : "New GeoServer store was created"
                    }}, status.HTTP_201_CREATED
                    
                elif r.status_code == 403:
                    wsref = f'Expected workspace {ws} but client specified null'

                    if wsref in txt:
                        response, http = {"status" : {
                            "code"    : "GS2",
                            "message" : "Workspace doesn't exist"
                        }}, status.HTTP_404_NOT_FOUND
                    
                    else:
                        response, http = rwrong, status.HTTP_400_BAD_REQUEST
                
                elif r.status_code == 500:
                    stref = f"Store '{rd['store']}' already exists in workspace '{ws}'"

                    if stref == txt:
                        response, http = {"status" : {
                            "code"    : "GS2",
                            "message" : "Store already exists"
                        }}, status.HTTP_404_NOT_FOUND
                    
                    else:
                        response, http = rwrong, status.HTTP_400_BAD_REQUEST
                    
                else:
                    response, http = rwrong, status.HTTP_400_BAD_REQUEST
            
            else:
                response, http = {"status" : {
                    "code"    : "GS1",
                    "message" : "Can't connect to GeoServer"
                }}, status.HTTP_400_BAD_REQUEST
        
        fresp = Response(response, status=http)

        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/{ws}/stores/',
            'service'  : 'geoserver-stores',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp


class GeoServerStore(APIView):
    """
    Get, edit, delete GeoServer Store
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, ws, st):
        """
        Method GET - Get a specific datastore
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        G = con_gsrv()
        
        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
            f'geoserver/rest/workspaces/{ws}/datastores/{st}/'
        )
        
        try:
            rqs = rqsts.get(
                url, headers={'Accept' : 'application/json'},
                auth=(G["USER"], G["PASSWORD"])
            )
                    
            if rqs.status_code == 404:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : rqs.content
                }}, status.HTTP_404_NOT_FOUND
            
            else: 
                response, http = {
                    "status" : {"code": "S20", "message" : "Data successfully returned"},
                    "data"   : rqs.json()['dataStore']
                }, status.HTTP_200_OK
            
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
    
        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/{ws}/store/{st}/',
            'service'  : 'geoserver-store',
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
    
    def delete(self, request, ws, st):
        """
        Method DELETE - Delete a specific GeoServer Store
        ---
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        G = con_gsrv()
        
        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}/'
            f'geoserver/rest/workspaces/{ws}/'
            f'datastores/{st}?recurse=true'
        )
        
        try: 
            r = rqsts.delete(url, auth=(G["USER"], G["PASSWORD"]))
            
            if r.status_code == status.HTTP_200_OK:
                response, http = {"status" : {
                    "code"    : "G23",
                    "message" : "GeoServer store was deleted"
                }}, status.HTTP_200_OK
            else:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : r.content
                }}, status.HTTP_404_NOT_FOUND
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/{ws}/store/{st}/',
            'service'  : 'geoserver-store',
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
