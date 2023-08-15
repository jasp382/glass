"""
Views to Manage Raster Datasets Files
"""

import datetime as dt
import pytz
from glass.pys.oss import del_file

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


class RstLayerFile(APIView):
    """
    Receive RasterDataset file - Save Geo Image
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    def post(self, request, rdset, layer):
        """
        Receive Raster file and save it
        """
        
        import os
        from firerest.settings     import GEOMEDIA, DATABASES
        from glass.it.rst        import rsts_to_gpkg
        from glass.pys.oss         import del_file
        from glass.prop.rst        import get_cellsize
        from glass.prop.rst        import rst_ext
        from glass.prop.prj        import rst_epsg
        from glass.gp.ovl.sql.bbox import geoms_equal_to_bound
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        db = DATABASES["default"]["NAME"]

        # Check if Raster dataset exists
        if not _status:
            try:
                rdset = RasterDatasets.objects.get(slug=rdset)
            except RasterDatasets.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Dataset does not exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Check if Layer exists
        if not _status:
            try:
                lyr = RasterLayers.objects.get(layer=layer)
                lsrl = RasterLayerSrl(lyr)
                lyrd = lsrl.data
            
            except RasterLayers.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Layer does not exist"
                }, status.HTTP_404_NOT_FOUND
        
        # Receive Raster and check the EPSG code
        if not _status:
            fdata = request.FILES.get('dsetfile')

            rfile = os.path.join(
                GEOMEDIA, 'rdsetfile', f"{layer}.tif"
            )
            with open(rfile, 'wb+') as rf:
                for chunk in fdata.chunks():
                    rf.write(chunk)
            
            # Check epsg
            epsg = rst_epsg(rfile)
            
            if epsg != 3763:
                _status, http = {
                    "code"    : "E10",
                    "message" : (
                        "Raster SRS is not valid. "
                        "Raster EPSG code must be 3763"
                    )
                }, status.HTTP_400_BAD_REQUEST
        
        # Check overlay with ref cells
        if not _status:
            left, right, bottom, top = rst_ext(rfile)

            q_gid = geoms_equal_to_bound(
                db, "georef_refgrid", "geom", 3763,
                (left, top),
                (right, bottom), 3763
            )

            if q_gid.shape[0] == 0:
                _status, http = {
                    "code"    : "E11",
                    "message" : "Raster doesn't intersect with any cell"
                }, status.HTTP_400_BAD_REQUEST
            
            elif q_gid.shape[0] > 1:
                _status, http = {
                    "code"    : "E11",
                    "message" : "Raster intersects with more than one cell"
                }, status.HTTP_400_BAD_REQUEST
        
        # Add Raster to GeoPackage
        if not _status:
            # Add raster to GeoPackage
            # Create it if not exists
            gpkg = os.path.join(
                GEOMEDIA, 'gpkg', rdset.slug + '.gpkg' 
            )

            # geopackage update (add layer)
            rcmd = rsts_to_gpkg([rfile], gpkg, layers=[layer])
       
            #Get cell sizes
            cellsizex, cellsizey = get_cellsize(rfile)

            lyrd["cellsizex"] = cellsizex
            lyrd["cellsizey"] = cellsizey
            lyrd["refgrid"] = q_gid['gid'].values[0], #get the df value
            lyrd["idrst"] = rdset.id
            
            srl = RasterLayerSrl(lyr, data=lyrd)
            
            if srl.is_valid():           
                srl.save()
                
                # Delete temporary file
                del_file(rfile)

                response = srl.data
                response["status"] = {
                    "code"    : "S22",
                    "message" : "Dataset data was updated"
                }
                http = status.HTTP_201_CREATED
                
            else:
                response = {"status": {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}

                http = status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fr = Response(response, status=http)

        # Write logs
        li = LogsGeoRstSrl(data={
            'url'      : f'georst/raster-file/{str(rdset)}/{str(layer)}/',
            'service'  : 'manage-raster-file',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'cuser'    : request.user.pk,
            'data'     : None
        })

        if li.is_valid(): li.save()

        return fr

