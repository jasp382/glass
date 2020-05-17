"""
Do things with GeoPandas Geometries
"""

from geoalchemy2 import WKTElement
from shapely.geometry.multipoint import MultiPoint
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.multipolygon import MultiPolygon


def force_multipart(df, geomcol, epsg, gtype=None, r_wkt=True):
    """
    Force geometry to MultiPart
    """

    from glass.prop.feat import get_gtype

    def sanitize_geom(geom, GeomClass, epsg):
        if geom.geom_type.startswith('Multi') and r_wkt:
            return WKTElement(geom.wkt, srid=epsg)
            
        elif geom.geom_type.startswith('Multi') and not r_wkt:
            return geom
        
        elif not geom.geom_type.startswith('Multi') and not r_wkt:
            return GeomClass([geom])
        
        else:
            return WKTElement(GeomClass([geom]).wkt, srid=epsg)
        
    geom_type = get_gtype(
        df, name=True, py_cls=False, gisApi='pandas'
    ) if not gtype else gtype

    if geom_type.startswith('Multi'):
        MultiClass = MultiPolygon if geom_type == 'MultiPolygon' else \
            MultiLineString if geom_type == 'MultiLineString' else MultiPoint
        
        df[geomcol] = df[geomcol].apply(lambda x: sanitize_geom(x, MultiClass, epsg))
    
    return df
