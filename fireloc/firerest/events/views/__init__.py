"""
Fire events views
"""

import datetime as dt
import pytz


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from authapi.utils import id_usertype
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from events.srl       import YearSrl
from events.models    import Years

from logs.srl import LogsEventSrl


class ManYears(APIView):
    """
    Manage Years
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all Years
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        ey = Years.objects.all()
        srl = YearSrl(ey, many=True)

        response, http  = {
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/years/',
            'service'  : 'manage-years',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    

    def post(self, request):
        """
        Method POST - Add new year
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        data, pp = request.data, ["year"]

        _status, http = check_rqst_param(pp, list(data.keys()))
 
        if not _status:
            srl = YearSrl(data=data)
            if srl.is_valid():
                srl.save()
                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Event Year added."
                }, status.HTTP_201_CREATED
                
            else:
                response, http = {"status":{
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status}
    
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/years',
            'service'  : 'manage-years',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(data[k])}" for k in data]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request):
        """
        Method DELETE - Delete all years
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)


        # Get user and user type
        cuser, _status, http = request.user, None, None
        ustype = id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            Years.objects.all().delete()
            
            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Event Years deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
    
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/years',
            'service'  : 'manage-years',
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


class ManYear(APIView):
    """
    Manage Year
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, year):
        """
        Method GET - Retrieve Year
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            y = Years.objects.get(year=year)
        except Years.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Year doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = YearSrl(y)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/year/{str(year)}/',
            'service'  : 'manage-year',
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
    

    def put(self, request, year):
        """
        Method PUT - update year
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["year"]

        try:
            y = Years.objects.get(year=year)
            srl = YearSrl(y)
            srldata = srl.data
        
        except Years.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Event Year doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
                      
            srl = YearSrl(y, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response['_status'], http = {
                    "code"    : "S22",
                    "message" : "Event Year was updated."
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
        logsrl = LogsEventSrl(data={
            'url'      : f'events/year/{str(year)}/',
            'service'  : 'manage-year',
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
    
    def delete(self, request, year):
        """
        Method DELETE - Delete a specific Year
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            y = Years.objects.get(year=year)
        except Years.DoesNotExist:
            _status, http = {
                "code"    : "E03",
                "message" : "Event Year doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            y.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Event Year deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/year/{str(year)}/',
            'service'  : 'manage-year',
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

