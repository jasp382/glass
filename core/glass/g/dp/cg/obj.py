"""
Change Geometry types
"""

def multipart_to_single(df, geomType):
    """
    Multipart Geometries to SinglePart Geometries
    """
    
    import geopandas
    import pandas
    
    df_wsingle = df[df.geometry.type == geomType]
    df_wmulti  = df[df.geometry.type == 'Multi' + geomType]
    
    for i, row in df_wmulti.iterrows():
        series_geom = pandas.Series(row.geometry)
        
        ndf = pandas.concat([geopandas.GeoDataFrame(
            row, crs=df_wmulti.crs).T]*len(series_geom), ignore_index=True)
        
        ndf['geometry'] = series_geom
        
        df_wsingle = pandas.concat([df_wsingle, ndf])
    
    df_wsingle.reset_index(inplace=True, drop=True)
    
    return df_wsingle


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
        from glass.g.prj.obj import df_prj
        
        convexDf = df_prj(convexDf, outEpsg)
    
    if outShp:
        from glass.g.wt.shp import df_to_shp
        
        return df_to_shp(convexDf, outShp)
    
    return convexDf

