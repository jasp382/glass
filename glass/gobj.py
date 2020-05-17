from osgeo import ogr

#from django.contrib.gis.geos import GEOSGeometry

from glass.prj.obj import prj_ogrgeom

"""
Create Geometries
"""

def new_pnt(x, y):
    """
    Return a OGR Point geometry object
    """
    
    pnt = ogr.Geometry(ogr.wkbPoint)
    pnt.AddPoint(float(x), float(y))
    
    return pnt


def create_polygon(points, api='ogr'):
    """
    Return a OGR Polygon geometry object

    api options:
    * ogr;
    * shapely;
    """

    if api == 'shapely':
        from shapely.geometry import Polygon

        polygon = Polygon(points)

        return polygon
    
    else:
        ring = ogr.Geometry(ogr.wkbLinearRing)
    
        for pnt in points:
            if type(pnt) == tuple or type(pnt) == list:
                ring.AddPoint(pnt[0], pnt[1])
            else:
                ring.AddPoint(pnt.GetX(), pnt.GetY())
    
        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(ring)
    
    return polygon


def wkt_to_geom(wktTxt, withSpecialChar=None):
    """
    WKT to Geometry
    """
    
    if withSpecialChar:
        wktTxt = wktTxt.replace('v', ',').replace('e', ' ').replace(
            'p', '.').replace('f', '(').replace('u', ')')
    
    geom = ogr.CreateGeometryFromWkt(wktTxt)
    
    return geom


def polygon_to_multipolygon(wkt):
    """
    Polygon to MultiPolygon
    """

    from shapely.wkt import loads
    from shapely.geometry.multipolygon import MultiPolygon

    geom = loads(wkt)

    if geom.geom_type == 'Polygon':
        ngeom = MultiPolygon([geom])
    elif geom.geom_type == 'MultiPolygon':
        ngeom = geom
    else:
        ngeom = None
    
    return ngeom if not ngeom else ngeom.wkt


def gext_to_polygon(wkt):
    """
    Geometry bounding box to Polygon
    """

    g = ogr.CreateGeometryFromWkt(wkt)

    left, right, bottom, top = g.GetEnvelope()

    ext_geom = create_polygon([
        (left, top),
        (right, top),
        (right, bottom),
        (left, bottom),
        (left, top)
    ], api='ogr')

    return ext_geom.ExportToWkt()


def get_centroid(wkt, epsg=None, reprj=None, rgeos=None):
    """
    Get Geometry Centroid
    """

    geom = wkt_to_geom(wkt)

    if not geom: return None

    g = geom.Centroid()

    if reprj:
        g = prj_ogrgeom(g, epsg, reprj, api="shply")
    
    g.FlattenTo2D()

    nwkt = g.ExportToWkt()

    if not rgeos: return nwkt

    else:
        if epsg and reprj:
            return GEOSGeometry(nwkt, srid=reprj)
        
        elif epsg and not reprj:
            return GEOSGeometry(nwkt, srid=epsg)
        
        else:
            raise ValueError((
                "To return GEOSGeometry, you need to define "
                "epsg parameter"
            ))


def wkt_sanitize(wkt, epsg=None, reprj=None, rgeos=None):
    """
    Sanitize Geometries - Make it good to django models
    """

    geom = wkt_to_geom(wkt)

    if not geom: return None

    if reprj:
        geom = prj_ogrgeom(geom, epsg, reprj, api="shply")

    geom.FlattenTo2D()

    nwkt = geom.ExportToWkt()

    if not rgeos:
        return nwkt
    else:
        if epsg and reprj:
            return GEOSGeometry(nwkt, srid=reprj)
        elif epsg and not reprj:
            return GEOSGeometry(nwkt, srid=epsg)
        
        else:
            raise ValueError((
                "To return GEOSGeometry, you need to define "
                "epsg parameter"
            ))

