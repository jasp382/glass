"""
Manage Layers Legend
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

from firerest.permcls  import IsFireloc
from firerest.utils import check_rqst_param

from geovis.srl import MapLegSrl
from geovis.models import MapLayers, MapsLegend

from logs.srl import LogsGeovisSrl
from authapi.utils import id_usertype


class ManLegend(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve existing legend objects
        """

        tz = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime = tz.localize(_daytime)

        map_legends = MapsLegend.objects.all()
        srl = MapLegSrl(map_legends, many=True)

        code, msg = "S20", "Data successfully returned"

        rr = Response({
            "status": {"code": code, "message": msg},
            "data": srl.data
        }, status=status.HTTP_200_OK)

        log_i = LogsGeovisSrl(data={
            'url'      : 'geovis/layers-legend/',
            'service'  : 'manage-maps_legend',
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
        pr = ["color", "label", "order", "layerid"]

        # Check if we have all mandatory parameters in the request.data
        _status, http = check_rqst_param(pr, list(rd.keys()))

        # Check if we have cat, minval and maxval
        if not _status:
            rd["cat"]    = None if "cat" not in rd else rd["cat"]
            rd["minval"] = None if "minval" not in rd else rd["minval"]
            rd["maxval"] = None if 'maxval' not in rd else rd["maxval"]

            if rd["cat"]:
                rd["minval"] = None
                rd["maxval"] = None
            
            else:
                if not rd["minval"] or not rd["maxval"]:
                    _status, http = {
                        "code"    : "E01",
                        "message" : "minval and maxval must be given together"
                    }, status.HTTP_400_BAD_REQUEST
        
        # Check if the layer exists
        if not _status:
            try:
                lyr = MapLayers.objects.get(slug=rd['layerid'])

                rd['layerid'] = lyr.id
        
            except MapLayers.DoesNotExist:
                _status, http = {"status" : {
                    "code"    : "I03",
                    "message" : "Layer doesn't exist."
                }}, status.HTTP_404_NOT_FOUND

        # Check if exists
        if not _status:
            try:
                mapleg = MapsLegend.objects.get(
                    label=rd['label'], layerid=rd['layerid']
                )

                _status, http = {
                    "code"    : "I02",
                    "message" : "Legend already registed"
                }, status.HTTP_400_BAD_REQUEST

            except MapsLegend.DoesNotExist:
                pass

        # Create new Map Legend
        if not _status:
            srl = MapLegSrl(data=rd)
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
            'url'      : 'geovis/layers-legend/',
            'service'  : 'manage-maps_legend',
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
        Method DELETE - Delete all layers
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
            MapsLegend.objects.all().delete()

            response, http = {"status": {
                "code"    : "S24",
                "message" : "Legends deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status": _status}

        fr = Response(response, status=http)

        # Write Logs
        li = LogsGeovisSrl(data={
            'url'      : 'geovis/layers-legend/',
            'service'  : 'manage-maps_legends',
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


class LegEntrance(APIView):

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
            leg = MapsLegend.objects.get(pk=legid)
        except MapsLegend.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Legend Doesn't Exist"
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            srl = MapLegSrl(leg, many=False)

            response = srl.data

            response["status"], http = {
                "code" : "S20",
                "message" : "Data succesfully returned.",
            }, status.HTTP_200_OK

        else:
            response = {"status": _status}
        
        r = Response(response, status=http)

        log_get = LogsGeovisSrl(data={
            'url'      : f'geovis/layers-legend{legid}/',
            'service'  : 'manage_map_legends',
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

        atts = ["cat", "minval", "maxval", "color", "label", "order", "layerid"]

        try:
            leg = MapsLegend.objects.get(pk=legid)
            lsrl = MapLegSrl(leg)
            ld   = lsrl.data
        
        except MapsLegend.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Legend Doesn't Exist"
            }, status.HTTP_404_NOT_FOUND
        

        if not _status:
            for a in atts:
                if a == 'layerid' and a in rd:
                    try:
                        lyr = MapLayers.objects.get(slug=rd['layerid'])

                        rd[a] = lyr.id

                        continue
        
                    except MapLayers.DoesNotExist:
                        _status, http = {"status" : {
                            "code"    : "I03",
                            "message" : "Layer doesn't exist."
                        }}, status.HTTP_404_NOT_FOUND

                        break
                
                if a not in rd:
                    rd[a] = ld[a]
        
        if not _status:
            srl = MapLegSrl(leg, data=rd)
                
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
            'url'      : f'geovis/legend-i/{legid}/',
            'service'  : 'manage-legend-entrance',
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
            legend = MapsLegend.objects.get(id=legid)
        except MapsLegend.DoesNotExist:
            _status, http = {
                "code": "I01",
                "message": "Legend Does Not Exist"
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            legend.delete()

            response, http = {"status": {
                "code": "S24",
                "message": "Legend Deleted"
            }}, status.HTTP_200_OK
        else:
            response = {"status": _status}

        rr = Response(response, status=http)

        log_delete = LogsGeovisSrl(data = {
            'url'       : f'geovis/legend-i/{legid}/',
            'service'   : 'manage-legend-entrance',
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

