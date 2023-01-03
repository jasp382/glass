from osgeo import ogr

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

