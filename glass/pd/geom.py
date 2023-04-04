"""
Do things with GeoPandas Geometries
"""

from geoalchemy2 import WKTElement
from shapely.geometry.multipoint import MultiPoint
from shapely.geometry.multilinestring import MultiLineString
from shapely.geometry.multipolygon import MultiPolygon


def force_multipart(df, geomcol, geom_type, epsg):

    def sanitize_geom(geom, GeomClass, epsg):
        if geom.geom_type.startswith('Multi'):
            return WKTElement(geom.wkt, srid=epsg)
        
        else:
            return WKTElement(GeomClass([geom]).wkt, srid=epsg)
    
    if geom_type.startswith('Multi'):
        MultiClass = MultiPolygon if geom_type == 'MultiPolygon' else \
            MultiLineString if geom_type == 'MultiLineString' else MultiPoint
        
        df[geomcol] = df[geomcol].apply(lambda x: sanitize_geom(x, MultiClass, epsg))
    
    else:
        df[geomcol] = df[geomcol].apply(lambda x: WKTElement(x.wkt, srid=epsg))
    
    return df
