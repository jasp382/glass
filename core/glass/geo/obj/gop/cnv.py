"""
Conversion Operations with Python Objects
"""

def multipart_to_single(inDf, geomType):
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

