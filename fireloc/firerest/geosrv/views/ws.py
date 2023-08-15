"""
SDI related Views
"""

import datetime as dt
import pytz
import requests as rqsts
import json

# REST Framework Dependencies
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc
from firerest.utils    import check_rqst_param

from logs.srl import LogsSDISrl

from glass.firecons.gsrv import con_gsrv

################################################################################
# ######################## GeoServer - Workspaces ##############################
################################################################################

class GeoServerWorkspaces(APIView):
    """
    List/Create Workspace in our GeoServer Instance
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve a list with all existing Workspaces in GeoServer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G, msg = con_gsrv(), "Data successfully returned"

        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}'
            f':{G["PORT"]}/geoserver/rest/workspaces'
        )

        try:
            gsrv_r = rqsts.get(
                url, headers={'Accept' : 'application/json'},
                auth=(G['USER'], G['PASSWORD'])
            )

            if gsrv_r.status_code == 200:
                rsp = [] if gsrv_r.json()['workspaces'] == '' else \
                    gsrv_r.json()['workspaces']['workspace']

                response, sc = {
                    "status" : {"code" : "S20", "message" : msg},
                    "data"   : rsp
                }, status.HTTP_200_OK
            
            else:
                response, sc = {"status" : {
                    "code"    : "GS2",
                    "message" :  gsrv_r.content
                }}, status.HTTP_404_NOT_FOUND
        
        except:
            response, sc = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        fresp = Response(response, status=sc)
        
        li = LogsSDISrl(data={
            'url'      : 'geosrv/workspaces/',
            'service'  : 'geoserver-workspaces',
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
        Method POST - Create new workspace in GeoServer
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        data, G = request.data, con_gsrv()

        # Check if parameters are valid
        _status, http = check_rqst_param(["workspace"], data)
        
        if not _status:
            url = (
                f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}'
                f'/geoserver/rest/workspaces'
            )

            try:
                rgsrv = rqsts.post(
                    url,
                    data=json.dumps({'workspace': {'name' : data["workspace"]}}),
                    headers={'content-type': 'application/json'},
                    auth=(G['USER'], G['PASSWORD'])
                )

                if rgsrv.status_code == 201:
                    msg = "New GeoServer workspace was created"
                    response, http = {
                        "status" : {"code": "G21", "message" : msg},
                        "data"   : {'workspace' : data['workspace']}
                    }, status.HTTP_201_CREATED
                
                else:
                    response, http = {"status" : {
                        "code"    : "GS2",
                        "message" : "Workspace already exists",
                    }}, status.HTTP_400_BAD_REQUEST
        
            except:
                response, http = {"status" : {
                    "code"    : "GS1",
                    "message" : "Can't connect to GeoServer"
                }}, status.HTTP_400_BAD_REQUEST
        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)

        log = LogsSDISrl(data={
            'url'      : 'geosrv/workspaces/',
            'service'  : 'geoserver-workspaces',
            'http'     : fresp.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(data[k])}" for k in data]),
            'method'   : request.method,
            'cuser'    : request.user.pk
        })

        if log.is_valid(): log.save()

        return fresp


class GeoServerWorkspace(APIView):
    """
    Get, edit, delete GeoServer Workspace
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, ws):
        """
        Method GET - Retrive a specific Workspace
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        G = con_gsrv()
        
        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:{G["PORT"]}'
            f'/geoserver/rest/workspaces/{ws}/'
        )

        # Request to GeoServer
        try:
            ws_request = rqsts.get(
                url,
                headers={'content-type': 'application/json'},
                auth=(G['USER'], G['PASSWORD'])
            )
                    
            if ws_request.status_code == 200:
                msg = "Data successfully returned"
                response, http = {
                    "status" : {"code" : "S20", "message" : msg},
                    "data"   : ws_request.json()
                }, status.HTTP_200_OK
            
            else:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : ws_request.content
                }}, status.HTTP_404_NOT_FOUND
        
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        rrr = Response(response, status=http)
        
        # Write Logs
        log = LogsSDISrl(data={
            'url'      : f'geosrv/workspace/{ws}/',
            'service'  : 'geoserver-workspace',
            'method'   : request.method,
            'http'     : rrr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log.is_valid(): log.save()
        
        return rrr

    def delete(self, request, ws):
        """
        Method DELETE - Delete a specific workspace
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        G = con_gsrv()
        
        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
            f"geoserver/rest/workspaces/{ws}?"
            f"recurse=true"
        )

        try:
            r = rqsts.delete(url, auth=(G["USER"], G["PASSWORD"]))
            
            if r.status_code == 200:
                response, http = {"status" : {
                    "code"    : "G23",
                    "message" : "GeoServer workspace was deleted"
                }}, status.HTTP_200_OK
                
            else:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : "Workspace doesn't exist"
                }}, status.HTTP_404_NOT_FOUND
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        rr = Response(response, status=http)
        
        # Write Logs
        log = LogsSDISrl(data={
            'url'      : f'geosrv/workspace/{ws}/',
            'service'  : 'geoserver-workspace',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log.is_valid(): log.save()
        
        return rr
