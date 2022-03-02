from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

# Create your views here.

class GetOsmExtract(APIView):
    """
    Extract OSM Data from OSM Larger Files
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        return Response({
            "status"  : 403,
            "message" : "GET requests are not allowed"
        }, status=status.HTTP_403_FORBIDDEN)
    
    def post(self, request, whatdo, format=None):
        import os
        from api.settings         import DATABASES
        from osmapi               import OSM_PATH, OSM_EXTRACTS
        from gasp.sql.fm          import q_to_obj
        from gasp.g.to            import shpext_to_boundary
        from gasp.gt.gop.osm.ovly import osm_extraction
        from gasp.pyt.oss         import fprop, mkdir
        from gasp.pyt.tm          import now_as_str

        con_db = DATABASES['default']
        tbl    = 'osmapi_osmcountries'
        whatdo = whatdo if whatdo == 'download' else 'get'

        # Request data
        data = request.data

        # Check if we have geometry
        if "geom" not in data:
            return Response({
                "status" : 400,
                "detail" : "POST parameter geom was not in the request"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create folder for temporary files
        fld = mkdir(os.path.join(OSM_EXTRACTS, now_as_str()))

        # Get OSM Countries Files to use
        osmdf = q_to_obj(con_db, (
            "SELECT continent, country FROM "
            "{} WHERE ST_Intersects(geom, "
            "ST_GeomFromText('{}', 4326))"
        ).format(tbl, data["geom"]))
        
        if not osmdf.shape[0]:
            # No OSM Files were found
            return Response({
                "status" : 400,
                "detail" : "No OSM Files matching given boundary"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract OSM Data
        osm_extracts = [osm_extraction(
            data["geom"], os.path.join(
                OSM_PATH, row.continent,
                row.country + "-latest.osm.pbf"
            ), os.path.join(fld, 'osm_{}.xml'.format(str(idx)))
        ) for idx, row in osmdf.iterrows()]

        if not len(osm_extracts):
            # No files were produced
            # Something went wrong
            return Response({
                "status" : 400,
                "detail" : "Something went wrong when producing your files"
            }, status=status.HTTP_400_BAD_REQUEST)

        if whatdo == 'get':
            dresp = [{
                "continent" : row.continent,
                "country"   : row.country,
                "osm-file"  : "osm_{}.xml".format(str(idx))
            } for idx, row in osmdf.iterrows()]

            return Response(dresp)
        
        else:
            from gasp.web.djg.ff.down import down_xml

            if len(osm_extracts) == 1:
                return down_xml(osm_extracts[0])
            
            else:
                from gasp.gt.toshp.osm import osm_merge

                nosm = osm_merge(osm_extracts, os.path.join(
                    OSM_EXTRACTS, os.path.basename(fld) + '.xml'
                ))

                return down_xml(nosm)

