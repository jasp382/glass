"""
Manage Map Services  - Fire Detection procedures
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

from geovis.models import EventsLayers, EventsMapLeg
from events.models import RealFireEvents
from geovis.srl import MapRFireSrl, RealFireLegSrl
from logs.srl import LogsGeovisSrl



class ManFireLyrs(APIView):
    """
    Deal with geoserver services to present
    information of real fires events
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]


    def get(self, request):
        """
        Method GET - Retrieve all services
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        flyr = EventsLayers.objects.all()
        srl  = MapRFireSrl(flyr, many=True)

        code, mess = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }

        rr = Response(response, status=status.HTTP_200_OK)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/fire-events-layers/',
            'service'  : 'manage-fireevents-layers',
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
        Method POST - Add new fire event layer
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d = request.data

        # Expected request parameters
        # param as key; max_length as value
        rp = {
            "slug" : 15, "design" : 100, "work": 20,
            "store" : 20, "glyr": 40, "style": 20
        }

        pp = list(rp.keys()) + ["fireid"]

        # Check if we have all parameters
        _status, http = check_rqst_param(pp, list(d.keys()))

        # See if floc exists
        if not _status:
            try:
                f = RealFireEvents.objects.get(pk=int(d["fireid"]))
                d["fireid"] = f.id
            
            except RealFireEvents.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Fire Event instance doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        # Check parameters length
        if not _status:
            for _rp in rp:
                if len(d[_rp]) > rp[_rp]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {_rp} parameter is not valid "
                            f"(more than {str(rp[_rp])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Add to the database
        if not _status:
            srl = MapRFireSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "Fire Event Layer Created"
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
            'url'      : 'geovis/fire-events-layers/',
            'service'  : 'manage-fireevents-layers',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : ";".join([f'{k}={str(d[k])}' for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return rr
    
    def delete(self, request):
        """
        Method DELETE - Delete all fireloc layers
        ---
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
            EventsLayers.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "All layers were deleted"
            }}, status.HTTP_200_OK
        
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : 'geovis/fire-events-layers/',
            'service'  : 'manage-fireevents-layers',
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


class ManFireLyr(APIView):

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

        _status, http = None, None

        try:
            lyri = EventsLayers.objects.get(slug=lyr)
        
        except EventsLayers.DoesNotExist:
            _status, http = {"status" : {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }}, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = MapRFireSrl(lyri)

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
            'url'      : f'geovis/fire-event-layer/{lyr}/',
            'service'  : 'manage-fireevent-layer',
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
            "slug" : 15, "design" : 100, "work": 20,
            "store" : 20, "glyr": 40, "style": 20
        }

        rd = request.data

        try:
            i    = EventsLayers.objects.get(slug=lyr)
            isrl = MapRFireSrl(i)
            lyr_ = isrl.data
        
        except EventsLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Check parameters length
        if not _status:
            for p in rp:
                if p not in rd:
                    rd[p] = lyr_[p]
                    continue
                
                if p in rd and len(rd[p]) > rp[p]:
                    _status, http = {
                        "code" : "E06",
                        "message" : (
                            f"Value of {p} parameter is not valid "
                            f"(more than {str(rp[p])} chars)"
                        )
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        if not _status:
            # Update MapLayer
            srl = MapRFireSrl(i, data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Layer updated"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
            
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/fire-event-layer/{lyr}/',
            'service'  : 'manage-fireevent-layer',
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
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            lyr = EventsLayers.objects.get(slug=lyr)
        except EventsLayers.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            lyr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Layer deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/fire-event-layer/{lyr}/',
            'service'  : 'manage-fireevent-layer',
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


class ManRFireLegend(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve existing legend objects
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        leg = EventsMapLeg.objects.all()
        srl = RealFireLegSrl(leg, many=True)

        code, msg = "S20", "Data successfully returned"

        rr = Response({
            "status": {"code": code, "message": msg},
            "data": srl.data
        }, status=status.HTTP_200_OK)

        log_i = LogsGeovisSrl(data={
            'url'      : 'geovis/fire-events-legend/',
            'service'  : 'manage-fireev-legend',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()

        return rr

    def post(self, request):
        """
        Method POST - Add new lengend object
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        # Mandatory Parameters
        pr = ["color", "label", "order", "lyrid"]

        # Check if we have all mandatory parameters in the request.data
        _status, http = check_rqst_param(pr, list(rd.keys()))

        # Check if we have cat, minval and maxval
        if not _status:
            rd["cat"]    = None if "cat" not in rd else rd["cat"]
            rd["minval"] = None if "minval" not in rd else rd["minval"]
            rd["maxval"] = None if 'maxval' not in rd else rd["maxval"]

            if rd["cat"]:
                rd["minval"], rd["maxval"] = None, None
            
            else:
                if not rd["minval"] or not rd["maxval"]:
                    _status, http = {
                        "code"    : "E01",
                        "message" : "minval and maxval must be given together"
                    }, status.HTTP_400_BAD_REQUEST
        
        # Check if the layer exists
        if not _status:
            try:
                lyr = EventsLayers.objects.get(slug=rd['lyrid'])

                rd['lyrid'] = lyr.id
        
            except EventsLayers.DoesNotExist:
                _status, http = {"status" : {
                    "code"    : "I03",
                    "message" : "Layer doesn't exist."
                }}, status.HTTP_404_NOT_FOUND

        # Check if exists
        if not _status:
            try:
                mapleg = RealFireLegSrl.objects.get(
                    label=rd['label'], layerid=rd['layerid']
                )

                _status, http = {
                    "code"    : "I02",
                    "message" : "Legend already registed"
                }, status.HTTP_400_BAD_REQUEST

            except RealFireLegSrl.DoesNotExist:
                pass

        # Create new Map Legend
        if not _status:
            srl = RealFireLegSrl(data=rd)
            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Map Legend created!"
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status": {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status": _status}

        fr = Response(response, status=http)

        log_i = LogsGeovisSrl(data={
            'url'      : 'geovis/fire-events-legend/',
            'service'  : 'manage-fireev-legend',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response['status']['code'],
            'message'  : response['status']['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()

        return fr

    def delete(self, request):
        """
        Method DELETE - Delete all legend entrances
        """

        tz = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime = tz.localize(_daytime)

        _status, http = None, None

        cuser = request.user
        P = id_usertype(cuser)

        if P != 'superuser':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action"
            }, status.HTTP_403_FORBIDDEN

        if not _status:
            EventsMapLeg.objects.all().delete()

            response, http = {"status": {
                "code"    : "S24",
                "message" : "Legends deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status": _status}

        fr = Response(response, status=http)

        # Write Logs
        li = LogsGeovisSrl(data={
            'url'      : 'geovis/fire-events-legend/',
            'service'  : 'manage-fireev-legend',
            'http'     : fr.status_code,
            'code'     : response['status']['code'],
            'message'  : response['status']['message'],
            'datehour' : daytime,
            'data'     : None,
            'method'   : request.method,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fr


class RFireLegEntrance(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, legid):
        """
        Method GET - Retrieve a specific legend object
        """

        _status, http = None, None
        
        tz      = pytz.timezone('UTC')
        _dt     = dt.datetime.utcnow().replace(microsecond=0)
        daytime = tz.localize(_dt)

        try:
            leg = EventsMapLeg.objects.get(pk=legid)
        except EventsMapLeg.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Legend Doesn't Exist"
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            srl = RealFireLegSrl(leg, many=False)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data succesfully returned.",
            }, status.HTTP_200_OK

        else:
            response = {"status": _status}
        
        r = Response(response, status=http)

        log_get = LogsGeovisSrl(data={
            'url'      : f'geovis/fire-event-leg/{legid}/',
            'service'  : 'manage-fireev-legi',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log_get.is_valid(): log_get.save()

        return r

    def put(self, request, legid):
        """
        Method PUT - Edit Legend Layer
        """

        tz = pytz.timezone('UTC')
        _dt = dt.datetime.utcnow().replace(microsecond=0)
        daytime = tz.localize(_dt)

        rd = request.data

        atts = ["cat", "minval", "maxval", "color", "label", "order", "lyrid"]

        try:
            leg  = EventsMapLeg.objects.get(pk=legid)
            lsrl = RealFireLegSrl(leg)
            ld   = lsrl.data
        
        except EventsMapLeg.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Legend Doesn't Exist"
            }, status.HTTP_404_NOT_FOUND
        

        if not _status:
            for a in atts:
                if a == 'lyrid' and a in rd:
                    try:
                        lyr = EventsLayers.objects.get(slug=rd['lyrid'])

                        rd[a] = lyr.id

                        continue
        
                    except EventsLayers.DoesNotExist:
                        _status, http = {"status" : {
                            "code"    : "I03",
                            "message" : "Layer doesn't exist."
                        }}, status.HTTP_404_NOT_FOUND

                        break
                
                if a not in rd:
                    rd[a] = ld[a]
        
        if not _status:
            srl = RealFireLegSrl(leg, data=rd)
                
            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {    
                    "code": "S22",
                    "message": "Legend Updated Successfully"                   
                }, status.HTTP_200_OK

            else:
                response, http = {"status": {
                    "code": "Z01",
                    "message": srl.errors                 
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status": _status}

        rr = Response(response, status=http)

        log_set = LogsGeovisSrl(data={
            'url'      : f'geovis/fire-event-leg/{legid}/',
            'service'  : 'manage-fireev-legi',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={rd[k]}" for k in rd]),
            'cuser'    : request.user.pk
        })


        if log_set.is_valid(): log_set.save()

        return rr
    
    def delete(self, request, legid):
        """
        Method DELETE - Delete layer
        """

        timezone = pytz.timezone('UTC')
        currentTime = dt.datetime.utcnow().replace(microsecond=0)
        dateAndTime = timezone.localize(currentTime)

        _status, http = None, None

        try:
            legend = EventsMapLeg.objects.get(id=legid)
        except EventsMapLeg.DoesNotExist:
            _status, http = {
                "code": "I01",
                "message": "Legend Does Not Exist"
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            legend.delete()

            response, http = {"status": {
                "code"    : "S24",
                "message" : "Legend Deleted"
            }}, status.HTTP_200_OK
        else:
            response = {"status": _status}

        rr = Response(response, status=http)

        log_delete = LogsGeovisSrl(data = {
            'url'      : f'geovis/fire-event-leg/{legid}/',
            'service'  : 'manage-fireev-legi',
            'method'    : request.method,
            'http'      : rr.status_code,
            'code'      : response["status"]["code"],
            'message'   : response["status"]["message"],
            'datehours' : dateAndTime,
            'data'      : None,
            'cuser'     : request.user.pk
        })

        if log_delete.is_valid(): log_delete.save()

        return rr

