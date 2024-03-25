import os
import random

import geopandas as gp

from geoms.tools import wkt_sanitize

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from geoms.models import Geodata
from geoms.srl import GeodataSrl


def save_file(save_fld, _file):
    """
    Store a uploaded file in a given folder
    """ 
    
    file_out = os.path.join(save_fld, _file.name)
    with open(file_out, 'wb+') as destination:
        for chunk in _file.chunks():
            destination.write(chunk)
    
    return file_out


class ReceiveLayerFiles(APIView):
    """
    Receive Layer Files
    """

    def post(self, request, lyr):
        """
        Receive Layer Vetorial Data
        """

        cols = ['code', 'name', 'layerid', 'geom']

        d = request.data

        # Create a new folder to save files
        chars = '0123456789qwertyuiopasdfghjklzxcvbnm'
        numb = '0123456789'
        fname = ''
        fl = None
        for i in range(10):
            if not i:
                while not fl:
                    rc = random.choice(chars)

                    if rc in numb:
                        continue

                    else:
                        fl = True
            else:
                rc = random.choice(chars)

            fname += rc
        
        dfolder = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'layersdata', fname
        )
        os.mkdir(dfolder)

        files = request.FILES.getlist('shape[]')

        shp = None

        for f in files:
            save_file(dfolder, f)

            name, ff = os.path.splitext(f.name)

            if ff == '.shp':
                shp = os.path.join(dfolder, f.name)
        
        # Open Shapefile
        gdf = gp.read_file(shp)

        gdf.rename(columns={
            d['code']  : 'code',
            d['class'] : 'name' 
        }, inplace=True)

        gdf["layerid"] = lyr

        gdf["geom"] = gdf.geometry.to_wkt()

        gdf["geom"] = gdf.apply(lambda x: wkt_sanitize(x.geom, 3763), axis=1)

        gdf.drop([
            c for c in gdf.columns.values if c not in cols
        ], axis=1, inplace=True)

        gd = gdf.to_dict(orient="records")

        srl = GeodataSrl(data=gd, many=True)

        if srl.is_valid():
            srl.save()

            response = {"message" : "data was added with success"}
            http = status.HTTP_201_CREATED
        
        else:
            response = {"errors" : str(srl.errors)}
            http = status.HTTP_400_BAD_REQUEST

        return Response(response, status=http)


class ManGeoms(APIView):
    """
    Manage Existing Geometries
    """

    parser_classes = [JSONParser]

    def get(self, request, lid):
        """
        Retrieve geometries of a specific layer
        """

        geoms = Geodata.objects.filter(layerid=lid)
        srl = GeodataSrl(geoms, many=True)

        rsp = Response(srl.data, status=status.HTTP_200_OK)

        return rsp
    
    def delete(self, request, lid):

        geoms = Geodata.objects.filter(layerid=lid)

        geoms.delete()

        response = {'status' : 'All Geometries were deleted'}

        rr = Response(response, status.HTTP_200_OK)

        return rr


class ManGeom(APIView):
    """
    Manage existing geometry by id 
    """

    parser_classes = [JSONParser]

    def get(self, request, fid):
        _status, http = None, None

        try:
            geom = Geodata.objects.get(pk=int(fid))
        
        except Geodata.DoesNotExist:
            _status, http = {
                "message" : "Geometry doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = GeodataSrl(geom)

            response, http = srl.data, status.HTTP_200_OK
        
        else:
            response = _status
        
        rr = Response(response, status=http)

        return rr
