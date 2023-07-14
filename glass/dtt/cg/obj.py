"""
Change Geometry types
"""

def multipart_to_single(df, geomType, use_explode=True):
    """
    Multipart Geometries to SinglePart Geometries
    """
    
    import geopandas as gp
    import pandas as pd

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


def pntDf_to_convex_hull(pntDf, xCol, yCol, epsg, outEpsg=None, outShp=None):
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

