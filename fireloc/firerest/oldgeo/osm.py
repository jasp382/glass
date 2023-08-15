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
        from firerest.settings import DATABASES
        from glass.sql.q    import q_to_obj
        from glass.gp.ovl.osm import osm_extraction
        from glass.pys.oss    import mkdir
        from glass.pys.tm     import now_as_str

        OSM_EXTRACTS = ''
        OSM_PATH = ''

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
            f"{tbl} WHERE ST_Intersects(geom, "
            f"ST_GeomFromText('{data['geom']}', 4326))"
        ))
        
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
            ), os.path.join(fld, f'osm_{str(idx)}.xml')
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
                "osm-file"  : f"osm_{str(idx)}.xml"
            } for idx, row in osmdf.iterrows()]

            return Response(dresp)
        
        else:
            from glass.wg.djg.down import down_xml

            if len(osm_extracts) == 1:
                return down_xml(osm_extracts[0])
            
            else:
                from glass.it.osm import osm_merge

                nosm = osm_merge(osm_extracts, os.path.join(
                    OSM_EXTRACTS, os.path.basename(fld) + '.xml'
                ))

                return down_xml(nosm)

