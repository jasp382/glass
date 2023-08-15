"""
Views to Manage Raster Layers
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from firerest.utils import check_rqst_param
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc

from georst.models import RasterDatasets, RasterLayers
from georst.srl import RasterLayerSrl
from logs.srl import LogsGeoRstSrl

class RstLayers(APIView):
    """
    Receive RasterDataset file - Save Geo Image
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        List all Raster Layers
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        qp = request.query_params

        slugid = "all" if "rdataset" not in qp else qp["rdataset"]

        if slugid == 'all':
            lyrs = RasterLayers.objects.all()
        
        else:
            lyrs = RasterLayers.objects.filter(idrst__slug=slugid)
        
        srl = RasterLayerSrl(lyrs, many=True)

        code, msg = "S20", "Data successfully returned"

        response = {
            "status" : {"code" : code, "message ": msg},
            "data"   : srl.data
        }

        fr = Response(response, status=status.HTTP_200_OK)
        
        # Write LOGS
        li = LogsGeoRstSrl(data={
            'url'      : 'georst/raster-layers/',
            'service'  : 'manage-raster-layers',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'cuser'    : request.user.pk,
            'data'     : None
        })

        if li.is_valid(): li.save()

        return fr
    
    def post(self, request):
        """
        Add new layer
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get request data
        d = request.data

        # Mandatory request params
        rps = ["layer", "method", "rstdset"]

        # Check if all mandatory parameters are in the request
        _status, http = check_rqst_param(rps, list(d.keys()))

        # Check if Raster dataset exists
        if not _status:
            try:
                rdset = RasterDatasets.objects.get(slug=d["rstdset"])
            except RasterDatasets.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Dataset does not exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Add layer
        if not _status:
            d["idrst"] = rdset.id

            d["level"] = None if "level" not in d else d["level"]

            srl = RasterLayerSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Dataset data was updated"
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        fr = Response(response, status=http)

        # Write logs
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-layers/',
            'service'  : 'manage-raster-layers',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'cuser'    : request.user.pk,
            'data'     : ';'.join([f"{k}={str(d[k])}" for k in d])
        })

        if li.is_valid(): li.save()

        return fr

