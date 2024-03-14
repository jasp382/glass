
from osgeo import ogr

from django.contrib.gis.geos import GEOSGeometry


def wkt_sanitize(wkt, epsg):
    """
    Sanitize Geometries - Make it good to django models
    """

    geom = ogr.CreateGeometryFromWkt(wkt)

    if not geom: return None

    geom.FlattenTo2D()

    nwkt = geom.ExportToWkt()
    
    return GEOSGeometry(nwkt, srid=epsg)

