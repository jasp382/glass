"""
Users, Groups and Authentication related Views
"""

import datetime as dt
import pytz
import requests as rqsts

from drf_yasg import openapi

from django.contrib.auth.models import User

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from drf_yasg.utils import swagger_auto_schema

from glass.firecons.rest import rest_params

from firerest.settings import ADMIN_URL

from authapi.utils  import id_usertype
from firerest.utils import check_rqst_param

from logs.srl import LogsTokenSrl

################################################################################
# ############################# Authorization ##################################
################################################################################


class GetTokens(APIView):
    """
    Get access token
    """

    parser_classes = [JSONParser]

    @swagger_auto_schema(
        operation_summary="Create/Refresh Access Token",
        operation_description="Create/Refresh Access Token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'clientid': openapi.Schema(type=openapi.TYPE_STRING),
                'secret': openapi.Schema(type=openapi.TYPE_STRING),
                'userid': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),

            }
        )
    )

    def post(self, request, op, format=None):
        """
        Access tokens
        
        Create/refresh access token
        """

        tz = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime = tz.localize(_daytime)

        data, rp = request.data, rest_params()
        p, d, _p = rp["PROTOCOL"], rp["DOMAIN"], rp["PORT"]
        cli_id, sct_id = rp["CLIENT"], rp["SECRET"]

        # Check if parameters are valid
        _rp = ['token'] if op == 'renew' else ['password', 'userid']

        _status, http = check_rqst_param(_rp, data)
        
        if not _status:
            URL = f'{p}://{d}:{_p}/{ADMIN_URL}/o/token/'

            rdata = {
                'grant_type'    : 'refresh_token',
                'refresh_token' : data.get('token', None)
            } if op == 'renew' else {
                'grant_type' : 'password',
                'username'   : data.get('userid', None),
                'password'   : data.get('password', None)
            }

            r = rqsts.post(URL, data=rdata, auth=(cli_id, sct_id))

            odata = r.json()

            if "error" in odata:
                if odata['error'] == 'invalid_grant':
                    _status = {
                        "code"    : 'A01',
                        "message" : 'Wrong user or password'
                    }
                
                elif odata['error'] == 'invalid_client':
                    _status = {
                        "code"    : 'E03',
                        "message" : "User doesn't exist"
                    }
                
                else:
                    _status = {
                        "code"    : "UNK", 
                        "message" : odata["error"]
                    }

                http = status.HTTP_400_BAD_REQUEST

                response = {"status" : _status}
            
            else:
                response = odata

                response["status"] = {
                    "code"    : 'A21',
                    "message" : 'Access tokens were generated!'
                }

                if 'userid' in data:
                    cuser  = User.objects.get(username=data['userid'])
                    ustype = id_usertype(cuser)

                    response["role"] = ustype
            
                http = status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        f_response = Response(response, status=http)

        # Write logs
        logs_i = LogsTokenSrl(data={
            'url'      : f'auth/token/{op}/',
            'service'  : 'get-token',
            'http'     : f_response.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(data[k])}" for k in data if k != "password"
            ]),
            'method'   : request.method,
            'cuser'    : None
        })

        if logs_i.is_valid(): logs_i.save()

        return f_response

