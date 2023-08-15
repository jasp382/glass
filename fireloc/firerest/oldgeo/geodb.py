from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from rest_framework import permissions


from geo.srl    import DatasetsSerial, EventsSrl, DataTypesSrl, DataExtractsSrl
from geo.models import Datasets, ExtremeEvents, DatasetTypes, DataExtracts
from georef.models import RefGrid
from georef.srl import RefGridSrl


class RefGridView(APIView):
    """
    Get GRID Geometries
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        cells = RefGrid.objects.all()

        serializer = RefGridSrl(cells, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DatasetsList(APIView):
    """
    GET | POST Datasets Models
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        dt = Datasets.objects.all()
        serializer = DatasetsSerial(dt, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        serializer = DatasetsSerial(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DatatypesEndpoint(APIView):
    """
    Dataset types list
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        dt = DatasetTypes.objects.all()

        serializer = DataTypesSrl(dt, many=True)

        return Response(serializer.data)


class EventsList(APIView):
    def get(self, request, format=None):
        import json

        dt = ExtremeEvents.objects.all()
        serializer = EventsSrl(dt, many=True)

        return Response(serializer.data)


class DatasetExtract(APIView):
    """
    Receive a boundary in WKT and a dataset slug and
    provide a file with the data of that dataset for
    the specified area
    """

    permission_classes = [permissions.IsAdminUser]

    def wkt_sanitize(self, wkt, epsg):
        from osgeo      import ogr
        from glass.prj.obj import prj_ogrgeom

        geom = ogr.CreateGeometryFromWkt(wkt)

        if int(epsg) != 3763:
            geom = prj_ogrgeom(geom, epsg, 3763, api='shply')
        
        geom.FlattenTo2D()

        return geom.ExportToWkt()

    def get(self, request, format=None):
        d = {
            "status" : 403,
            "message" : "GET resquests are not allowed"
        }

        return Response(d, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request, format=None):
        import os
        from fireapi.settings import DATABASES
        from geo              import GPKG_FLD, REFGRID_TBL, GEODB_EXTRACTS
        from glass.sql.q import q_to_obj
        from glass.it.rst import gpkgrst_to_rst
        from glass.rst.mos   import rsts_to_mosaic
        from glass.pys.char  import random_str
        from glass.pys.tm    import now_as_str
        from glass.pys.oss   import mkdir, del_folder

        GEODB_MAIN_DIR = "TEMP"

        # Get Database name
        db = DATABASES['default']["NAME"]

        # Check if data folders are ready
        if not GEODB_MAIN_DIR or not GEODB_EXTRACTS:
            return Response({
                "status" : 400,
                'detail' : "DIRS are not configured"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get POST data
        data = request.data

        if "geom" not in data or "dataset" not in data or "epsg" not in data:
            return Response({
                "status" : 400,
                "detail" : "POST parameters geom and dataset were not in the request"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # Sanitize geometry
            data["geom"] = self.wkt_sanitize(data["geom"], data["epsg"])

            lmt_geom = data["geom"]
            dataset  = data["dataset"]
            data["token"] = random_str(4) + '_' + now_as_str()
        
        # Get dataset instance
        try:
            dataset_i = Datasets.objects.get(slug=dataset)
        except:
            # Dataset does not exist
            return Response({
                "status" : 400,
                "detail" : ("Given dataset does not exist")
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create folder for temporary files
        fld = mkdir(os.path.join(GEODB_EXTRACTS, data["token"]))

        # Get Intersecting CELLS
        Q = (
            "SELECT {ci} FROM ("
                "SELECT {ci}, (ST_Area(ST_Intersection({gc}, "
                    "ST_GeomFromText('{wkt}', 3763))) "
                    "/ ST_Area({gc}) * 100) AS i_area "
                "FROM {t} WHERE ST_Intersects({gc}, "
                    "ST_GeomFromText('{wkt}', 3763))"
            ") AS foo WHERE i_area > 1"
        ).format(
            ci=REFGRID_TBL["CELLID"], gc=REFGRID_TBL["GEOM"], t=REFGRID_TBL["TBL"],
            wkt=lmt_geom
        )
        cells = q_to_obj(db, Q)

        if not cells.shape[0]:
            # No cells finded
            return Response({
                "status" : 400,
                "detail" : (
                    "Given geometry is invalid. No cells were found"
                )
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # get datasource
        geosrc = dataset_i.storage

        if dataset_i.storage_type == 'gpkg':
            # Export data from geopackage
            rsts = [gpkgrst_to_rst(
                os.path.join(GEODB_MAIN_DIR, geosrc + '.gpkg'),
                f"cell__{str(row.cellid)}",
                os.path.join(fld, f'{geosrc}_{str(row.cellid)}.tif')
            ) for idx, row in cells.iterrows()]

            # Create new Mosaic
            rst_data = rsts_to_mosaic(rsts, os.path.join(
                GEODB_EXTRACTS, f"{os.path.basename(fld)}.tif"
            ), api='rasterio')
        
        else:
            # Export data from PostGIS database
            from glass.it.shp   import dbtbl_to_shp
            from glass.pys.zzip import zip_folder

            shp_data = dbtbl_to_shp(
                geosrc, " UNION ALL ".join([
                    f"SELECT * FROM cell_{str(row.cellid)}"
                for idx, row in cells.iterrows()]),
                "geom",
                os.path.join(fld, f"{geosrc}.shp"),
                tableIsQuery=True, inDB='psql', api='pgsql2shp', epsg=3763
            )

            zip_folder(fld, os.path.join(GEODB_EXTRACTS, os.path.basename(fld) + '.zip'))
        
        data["storage"] = 'tif' if dataset_i.storage_type == 'gpkg' else 'zip'

        # Delete folder
        del_folder(fld)

        # Record data in the database
        serializer = DataExtractsSrl(data=data)

        if serializer.is_valid():
            serializer.save()

            data = serializer.data

            return Response({
                "code"     : 201,
                "data"     : data,
                "message"  : "Dataset was produced and is available for download!"
            }, status=status.HTTP_201_CREATED)
        
        else:
            return Response({
                "message"    : "something went wrong",
                "data"       : serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


def download_dataset(request, token):
    """
    Download produced dataset
    """

    import os
    from geo import GEODB_EXTRACTS

    try:
        i = DataExtracts.objects.get(token=token)
    except:
        return Response({
            "message"   : "Requested file does not exist!"
        }, status=status.HTTP_404_NOT_FOUND)
    
    path_to_file = os.path.join(GEODB_EXTRACTS, "{}.{}".format(
        token, str(i.storage)
    ))

    if i.storage == 'tif':
        from glass.wg.djg.down import down_tiff as down_file
    
    else:
        from glass.wg.djg.down import down_zip as down_file

    return down_file(path_to_file)


class GetDatasetLegend(APIView):
    """
    Return Json Response with Legend data for one dataset
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, dataset, format=None):
        import os
        from geo import GPKG_FLD
        from glass.rd.shp import shp_to_obj

        dt = Datasets.objects.get(slug=dataset)
        serializer = DatasetsSerial(dt)

        data = serializer.data

        gpkg_rst = os.path.join(GPKG_FLD, data['rst_gpkg'] + '.gpkg')

        leg = shp_to_obj(gpkg_rst, lyr='legend')
        leg.drop(['geometry'], axis=1, inplace=True)
        leg = leg.to_dict(orient="records")

        rjson = {
            'dataset' : data['slug'], 
            'fields'  : ['lid', 'code', 'legend'],
            'legend'  : leg
        }

        return Response(rjson)

