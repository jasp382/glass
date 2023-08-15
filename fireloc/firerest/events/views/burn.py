"""
Burn Area by year
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

from glass.gobj import wkt_sanitize
from glass.pys import obj_to_lst

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from authapi.utils    import id_usertype

from events.models import BurnAreas, Years
from events.srl    import BurnedAreaSrl

from logs.srl import LogsEventSrl


class ManBurnedAreas(APIView):
    """
    Manage Burned Areas
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all Burned areas
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        code, msg = "S20", "Data successfully returned"

        ba = BurnAreas.objects.all()
        srl = BurnedAreaSrl(ba, many=True)

        response, http  = {
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/burned-areas/',
            'service'  : 'manage-burned-areas',
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
        Method POST - Add new burned area
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        pp, d = ["geom", "refstart", "refend", "years", "timezone"], request.data

        _status, http = check_rqst_param(pp, list(d.keys()))

        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Check if starttime and endtime values are valid
            for time in ["refend", "refstart"]:
                try:
                    tt = dt.datetime.strptime(d[time], '%Y-%m-%d')

                    _tz = pytz.timezone(d["timezone"])

                    d[time] = _tz.localize(tt)
                
                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"{time} has not the right format"
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
 
        if not _status:
            #Handling Geom Data
            d["geom"] = wkt_sanitize(
                d["geom"],
                epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                reprj=None if d["epsg"] == 3763 else 3763,
                rgeos=True
            )

            if not d["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        # Check if year's exists
        yids = []
        if not _status:
            years = obj_to_lst(d["years"])

            for y in years:
                try:
                    yo = Years.objects.get(year=y)

                    yids.append(yo)
                
                except Years.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Year {str(y)} doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break

        # Save Burned Area
        if not _status:
            srl = BurnedAreaSrl(data=d)
            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Burned Area Event added."
                }, status.HTTP_201_CREATED
                
            else:
                response, http = {"status":{
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        # Relate the burned area with the years it was burning
        if not _status:
            ba = BurnAreas.objects.get(pk=response["id"])
            
            for y in yids:
                ba.years.add(y)
            
        else:
            response = {"status" : _status}
    
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/burned-areas/',
            'service'  : 'manage-burned-areas',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request):
        """
        Method DELETE - Delete all burned area
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser, _status, http = request.user, None, None
        ustype, _status = id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            BurnAreas.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Burned Area Events deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/burned-areas/',
            'service'  : 'manage-burned-areas',
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


class ManBurnedArea(APIView):
    """
    Manage Burned Area
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, fid):
        """
        Method GET - Retrieve data of a burned area
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            ba = BurnAreas.objects.get(pk=fid)
        except BurnAreas.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Burned Area Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = BurnedAreaSrl(ba)

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
            'url'      : f'events/burned-area/{str(fid)}/',
            'service'  : 'manage-burned-area',
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
    

    def put(self, request, fid):
        """
        Method PUT - update existing burned area
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["geom", "refend", "refstart", 'years', 'replace']

        try:
            ba = BurnAreas.objects.get(pk=fid)
            srl = BurnedAreaSrl(ba)
            srldata = srl.data
        except BurnAreas.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Burned Area Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        # Check timezone
        warns = []
        if not _status and ("refend" in d or "refstart" in d):
            if "timezone" not in d:
                warns.append('datetimes will not be updated - timezone is missing')
            
            else:
                tzs = list(pytz.all_timezones)

                if d["timezone"] not in tzs:
                    _status, http = {
                        "code" : "E08",
                        "message" : "timezone is invalid"
                    }, status.HTTP_400_BAD_REQUEST

        nyears = []        
        if not _status:
            years = obj_to_lst(d["years"])

            for year in years:
                try:
                    y = Years.objects.get(year=year)
                    nyears.append(y)
                except Years.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Event Year doesn't exist."
                    }, status.HTTP_404_NOT_FOUND

                    break

        if not _status:
            for p in rp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = srldata[p]

                    warns.append('geom not updated - epsg code is missing')
                    continue

                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p],
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj=None if d["epsg"] == 3763 else 3763,
                        rgeos=True
                    )

                    if not d[p]:
                        d[p] = srldata[p]

                        warns.append('geom not updated - epsg code is missing')
                    
                    continue

                if p not in d:
                    d[p] = srldata[p]
                      
            srl = BurnedAreaSrl(ba, data=d)
            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"     : "S22",
                    "message"  : "Burned Area was updated.",
                    "warnings" : warns
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        if not _status and len(nyears): 
            d['replace'] = False if 'replace' not in d else d['replace']

            # Add years
            if not d['replace']:
                # Add years to burned areas
                for yy in nyears:
                    ba.years.add(yy)
                    
            else:
                # Replace years
                ba.years.clear()
                
                ba.years.set(nyears)
        
        else:
            response = {"status" : _status} 

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/burned-area/{str(fid)}/',
            'service'  : 'manage-burned-area',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, fid):
        """
        Method DELETE - Delete burned area
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            ba = BurnAreas.objects.get(pk=fid)
        except BurnAreas.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Burn Area Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            ba.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Burn Area Event deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/burned-area/{str(fid)}/',
            'service'  : 'manage-burned-area',
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

