"""
Views to password recovery
"""

import datetime as dt

import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from glass.pys.char import random_str
from glass.firecons.webapp import con_webapp
from glass.email import send_email

from firerest.utils import check_rqst_param

from authapi.html import HTML_PASS_RECOVERY

from django.contrib.auth.models import User
from authapi.models             import UserCodes
from authapi.srl                import UserSrl, UserCodeSrl

from logs.srl import LogsAuthSrl

from django.contrib.auth.hashers import make_password


class RqstPassRecovery(APIView):
    """
    Request Password Revcovery - Send e-mail to user with new password
    """

    parser_classes = [JSONParser]

    def put(self, request):
        """
        Send E-mail password recovery
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        wapp = con_webapp()
        apph, apphttp, appport = wapp["DOMAIN"], wapp["PROTOCOL"], wapp["PORT"]

        resetpass = f"{apphttp}://{apph}:{appport}/login/resetpass/?token="

        rd = request.data

        params = ["email"]

        _status, http = check_rqst_param(params, list(rd.keys()))

        # Check if user exists
        # Get user
        if not _status:
            try:
                user = User.objects.get(username=rd["email"])
            except User.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "User doesn't exist"
                }, status.HTTP_400_BAD_REQUEST
        
        # Generate token
        if not _status:
            token = random_str(50)

            # Save token
            srl = UserCodeSrl(data={
                "user_id"      : user.id,
                'token'        : token,
                "confirmation" : False
            })

            if srl.is_valid():
                srl.save()
            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                } , status.HTTP_400_BAD_REQUEST

        # Send e-mail
        if not _status:
            st = send_email(
                rd["email"], 
                'FireLoc - Password Recovery',
                HTML_PASS_RECOVERY.format(tk=token, url=resetpass),
                daytime.strftime("%m/%d/%Y %H:%M:%S")
            )
            
            if st <= 0:
                response, http = {"status" : {
                    "code"    : "X01",
                    "message" : "Not possible to send e-mail"
                }}, status.HTTP_400_BAD_REQUEST
            
            else:
                response, http = {"status" : {
                    "code"    : "X21",
                    "message" : "Password token was sended"
                }}, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}

        f_resp = Response(response, status=http)

        # Write Logs
        logs_i = LogsAuthSrl(data={
            'url'      : "auth/request-pass-recovery/",
            'service'  : 'request-password-recovery',
            'http'     : f_resp.status_code,
            'code'     : response['status']['code'],
            'message'  : response['status']['message'],
            'datehour' : daytime,
            'data'     : None,
            'method'   : request.method,
            'cuser'    : request.user.pk
        })

        if logs_i.is_valid(): logs_i.save()

        return f_resp


class PasswordRecovery(APIView):
    """
    Password Recovery View - checks if its valid
    """

    parser_classes = [JSONParser]
    
    def put(self, request):
        """
        Password recovery if token is valid
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, pp = request.data, ["token", 'password']

        _status, http = check_rqst_param(pp, list(d.keys()))
        
        # Get user
        if not _status:
            try:
                ut = UserCodes.objects.get(token=d["token"])
                
            except UserCodes.DoesNotExist:
                _status, http = {
                    "code"  : "X02",
                    "token" : "Token to recover password is not valid"
                }, status.HTTP_400_BAD_REQUEST
        
        # Get User and Change password
        if not _status:
            user = User.objects.get(id=ut.user_id.id)

            usrl = UserSrl(user)

            udata = usrl.data

            udata["password"] = make_password(d["password"])

            srl = UserSrl(user, data=udata)

            if srl.is_valid():
                srl.save()

                response = srl.data

                del response["password"]
            

                response["status"], http = {
                    "code"    : 'S22',
                    "message" : "User password was changed"
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, http)
        
        # Write Logs
        dlist = [f"{k}={str(d[k])}" for k in d if k != 'password']
        
        logi = LogsAuthSrl(data={
            'url'      : 'auth/userconfirmation/',
            'service'  : 'password-recovery',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : dlist,
            'cuser'    : None
        })

        if logi.is_valid(): logi.save()

        return rr

