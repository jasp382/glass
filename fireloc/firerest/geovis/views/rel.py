"""
Relate GeoSpatial Information with Groups
"""

import datetime as dt
from firerest.utils import check_rqst_param
import pytz
 
# Rest Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser
 
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
 
from firerest.permcls  import IsFireloc

from geovis.models import MapLayers

from authapi.utils import id_usertype

from logs.srl import LogsGeovisSrl
 
from django.contrib.auth.models import Group


################################################################################
# ####################### Relation Layers | User Groups ###################### #
################################################################################
 
class GLayersUsers(APIView):
 
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]
 
    def put(self, request, group):
        """
        Method PUT - Edit relation between group and geoportal layers
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, rd = None, None, request.data

        if "layers_add" not in rd and "layers_del" not in rd:
            _status, http = {
                "code"    : 'E01',
                "message" : (
                    "layers_add | layers_del - at least one of "
                    "these keys must be in the request"
                )
            }, status.HTTP_400_BAD_REQUEST
        
        # Get group object
        if not _status:
            try:
                gi = Group.objects.get(name=group)
            except Group.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "Group does not exist."
                }, status.HTTP_404_NOT_FOUND

        lyrs = {"layers_add" : [], "layers_del" : []}
        if not _status:
            rd["layers_add"] = [] if "layers_add" not in rd else rd["layers_add"]
            rd["layers_del"] = [] if "layers_del" not in rd else rd["layers_del"]

            for k in rd:
                if k != "layers_add" and k != "layers_del":
                    del rd[k]

            # Should the layer not exist, status is updated accordingly
            # returns error
            for k in rd:
                for slug in rd[k]:
                    try:
                        lyr = MapLayers.objects.get(slug=slug)
                        lyrs[k].append(lyr)
                
                    except MapLayers.DoesNotExist:
                        _status, http = {
                            "code"    : "I01",
                            "message" : "Layer does not exist."
                        }, status.HTTP_404_NOT_FOUND
                
                        break
                
                if _status: break
        
        if not _status:
            # Should the status be None, layers have been found
            # proceed with editing
            for l in lyrs["layers_add"]:
                l.usgroup.add(gi)
            
            for l in lyrs["layers_del"]:
                l.usgroup.remove(gi)
            
            response, http = {"status" : {
                "code"    : "S22",
                "message" : "Relations were edited"
            }}, status.HTTP_201_CREATED
        
        else:
            response = {"status": _status}
        
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/layers-groups/{group}/',
            'service'  : 'manage-rel-layer-groups',
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
    
    def delete(self, request, group):
        """
        Method DELETE - Delete relationships
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        if not _status:
            try:
                gi = Group.objects.get(name=group)

            except Group.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "Group was not found."  
                }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            gi.maplayers.clear()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Group-Layers relations deleted."
            }}, status.HTTP_200_OK
        
        else:
            response = {"status": _status}
        
        rr = Response(response, status=http)

        li = LogsGeovisSrl(data={
            'url'      : f'geovis/layers-groups/{group}/',
            'service'  : 'manage-rel-layer-groups',
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

