"""
Views to manage data related to the sun position

- Geocentric sun right ascension
- Geocentric sun declination
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

from firerest.utils   import check_rqst_param
from firerest.permcls import IsFireloc
from authapi.utils    import id_usertype

from detect.models import SunData
from detect.srl    import SunSrl, ReadSunSrl

from logs.srl import LogsFiredetectSrl


class ManSunData(APIView):
    """
    Manage Sun ascencion and declination data
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Retrieve Sun ascencion and declination data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, qp = None, None, request.query_params

        qdt, stime, etime = None, None, None

        # Sanitize datetimes
        if 'datetime' in qp:
            try:
                qdt = dt.datetime.strptime(qp['datetime'], '%Y-%m-%d-%H-%M-%S')

                qdt = tz.localize(qdt)
            
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" :  f"datetime is not valid (has not the right format)"
                }, status.HTTP_400_BAD_REQUEST
        else:
            if "startime" in qp and "endtime" in qp:
                try:
                    stime = dt.datetime.strptime(qp["startime"], '%Y-%m-%d-%H-%M-%S')
                    stime = tz.localize(stime)
                
                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"startime is not valid (has not the right format)"
                    }, status.HTTP_400_BAD_REQUEST
                
                try:
                    etime = dt.datetime.strptime(qp["endtime"], '%Y-%m-%d-%H-%M-%S')
                    etime = tz.localize(etime)
                
                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"endtime is not valid (has not the right format)"
                    }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            if qdt and not stime and etime:
                sundata = SunData.objects.filter(datehour=qdt)
            
            elif not qdt and stime and etime:
                sundata = SunData.objects.filter(
                    datehour__gte=stime).filter(datehour__lte=etime)
            
            else:
                sundata = SunData.objects.all()
        
        if not _status:
            srl = ReadSunSrl(sundata, many=True) if len(sundata) else None

            data = srl.data if len(sundata) else []

            code, mess = "S20", "Data successfully returned"

            response, http = {
                "status" : {"code" : code, "message" : mess},
                "data"   : data
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/sun-declination/',
            'service'  : 'manage-sun-data',
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
    
    def post(self, request):
        """
        Add new instance
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        pp = ["datehour", "ascension", "declination", "timezone"]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if rd["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        # Sanitize datetime
        if not _status:
            try:
                tz = pytz.timezone(rd["timezone"])

                tt = dt.datetime.strptime(rd["datehour"], '%Y-%m-%d %H:%M:%S')

                rd["datehour"] = tz.localize(tt)
            
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" :  f"datehour value isn't valid (has not the right format)"
                }, status.HTTP_400_BAD_REQUEST
        
        # Add data
        if not _status:
            rd["ascension"] = round(rd["ascension"], 5)
            rd["declination"] = round(rd["declination"], 5)

            srl  = SunSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Values added."
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
            'url'      : 'floc/sun-declination/',
            'service'  : 'manage-sun-data',
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
        Delete all FLoc attributes
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {"status" : {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }}, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            SunData.objects.all().delete()

            _status, htpp = {"status" : {
                "code"    : "S24",
                "message" : "Sun Data deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=htpp)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/sun-declination/',
            'service'  : 'manage-sun-data',
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

