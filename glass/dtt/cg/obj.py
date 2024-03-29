"""
Change Geometry types
"""

import geopandas as gp
import pandas as pd

def multipart_to_single(df, geomType, use_explode=True):
    """
    Multipart Geometries to SinglePart Geometries
    """

    if not use_explode:
        df_wsingle = df[df.geometry.type == geomType]
        df_wmulti  = df[df.geometry.type == 'Multi' + geomType]
    
        for i, row in df_wmulti.iterrows():
            series_geom = pd.Series(row.geometry)
        
            ndf = pd.concat([pd.DataFrame(row).T]*len(series_geom))
        
            ndf['geometry'] = series_geom
        
            df_wsingle = pd.concat([df_wsingle, ndf])
    
        df_wsingle.reset_index(inplace=True, drop=True)
        df_wsingle = gp.GeoDataFrame(
            df_wsingle, crs=df.crs, geometry=df_wsingle.geometry
        )
    
        return df_wsingle
    
    ndf = df.explode(index_parts=False)

    return ndf


def single_to_multipart(singlegeom, iswkt=None, out_wkt=None):
    """
    Array with single geometries to multi-type geometry
    """

    from osgeo import ogr

    ref_g = singlegeom[0] if not iswkt else \
        ogr.CreateGeometryFromWkt(singlegeom[0])

    gtype = ref_g.GetGeometryName()

    if gtype == 'POINT':
        ngeom = ogr.Geometry(ogr.wkbMultiPoint)
    
    elif gtype == 'LINESTRING':
        ngeom = ogr.Geometry(ogr.wkbMultiLineString)
    
    elif gtype == 'POLYGON':
        ngeom = ogr.Geometry(ogr.wkbMultiPolygon)
    
    for g in singlegeom:
        p = ogr.CreateGeometryFromWkt(g) if iswkt else g

        ngeom.AddGeometry(p)
    
    return ngeom if not out_wkt else ngeom.ExportToWkt()



def dfpnt_to_convex_hull(pntDf, xCol, yCol, epsg, outEpsg=None, outShp=None):
    """
    Create a GeoDataFrame with a Convex Hull Polygon from a DataFrame
    with points in two columns, one with the X Values, other with the Y Values
    """
    
    from scipy.spatial import ConvexHull
    from shapely       import geometry
    from geopandas     import GeoDataFrame
    
    hull = ConvexHull(pntDf[[xCol, yCol]])
    
    poly = geometry.Polygon([[
        pntDf[xCol].iloc[idx], pntDf[yCol].iloc[idx]
    ] for idx in hull.vertices])
    
    convexDf = GeoDataFrame(
        [1], columns=['cat'],
        crs='EPSG:' + str(epsg), geometry=[poly]
    )
    
    if outEpsg and outEpsg != epsg:
        from glass.prj.obj import df_prj
        
        convexDf = df_prj(convexDf, outEpsg)
    
    if outShp:
        from glass.wt.shp import df_to_shp
        
        return df_to_shp(convexDf, outShp)
    
    return convexDf



def centroid_dfgeoms(df, geom, epsg=None):
    """
    Retrieve centroids from Geometries in a
    GeoDataFrame
    """

    _df = df.copy(deep=True)

    _df[geom] = gp.GeoSeries(_df[geom].centroid)

    if epsg:
        _df = gp.GeoDataFrame(_df, geometry=geom, crs=f"EPSG:{str(epsg)}")
    
    return _df

