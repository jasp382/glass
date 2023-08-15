"""
Fire Location Assessment Approaches
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import wkt_sanitize

from firerest.utils import check_rqst_param
from firerest.permcls import IsFireloc
from authapi.utils import id_usertype
from detect.models import FirelocApproach

from detect.srl import FirelocApprSrl

from logs.srl import LogsFiredetectSrl


class ManFlocApproachs(APIView):
    """
    Manage Fie Location Approaches
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Fire location assessment approaches
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)


        attrs = FirelocApproach.objects.all()
        srl = FirelocApprSrl(attrs, many=True)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-approachs/',
            'service'  : 'manage-fireloc-approachs',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def post(self, request):
        """
        Add new Fire location assessment approach
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        pp = ["slug", "name", "description"]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        if not _status:
            srl = FirelocApprSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New FLoc approach created."
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST 

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-approachs/',
            'service'  : 'manage-fireloc-approachs',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request):
        """
        Delete all approaches
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            FirelocApproach.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Fireloc Approachs deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-approachs/',
            'service'  : 'manage-fireloc-approachs',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if logsrl.is_valid(): logsrl.save()
        return rr


class ManFlocApproach(APIView):
    """
    Manage Fie Location Approaches
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, slug):
        """
        Get attributes of one Fire location assessment approach
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = FirelocApproach.objects.get(slug=slug)
        except FirelocApproach.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Approach doesn't exist."
            }, status.HTTP_404_NOT_FOUND


        if not _status:
            srl = FirelocApprSrl(attr)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-approach/{str(slug)}',
            'service'  : 'manage-fireloc-approach',
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
    
    def put(self, request, slug):
        """
        Update attributes of one Fire location assessment approach
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["slug", 'name', 'description']

        try:
            fap    = FirelocApproach.objects.get(slug=slug)
            fasrl  = FirelocApprSrl(fap)
            fasrld = fasrl.data
        except FirelocApproach.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Fireloc Approach doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = fasrld[p]
       
            srl = FirelocApprSrl(fap, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "FLoc Approach was updated."
                }, status.HTTP_201_CREATED
            
            else:
                _status, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-approach/{str(slug)}',
            'service'  : 'manage-fireloc-approach',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, slug):
        """
        Delete one approach
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = FirelocApproach.objects.get(slug=slug)
        except FirelocApproach.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Approach doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Approach deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-approach/{str(slug)}',
            'service'  : 'manage-fireloc-approach',
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

