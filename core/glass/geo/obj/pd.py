"""
Play with GeoDataFrames
"""

def pnt_dfwxy_to_geodf(df, colX, colY, epsg):
    """
    Pandas Dataframe with numeric x, y columns
    to GeoDataframe
    
    Works Only for Points
    """
    
    from geopandas        import GeoDataFrame
    from shapely.geometry import Point
    
    geoms = [Point(xy) for xy in zip(df[colX], df[colY])]
    df.drop([colX, colY], axis=1, inplace=True)
    gdata = GeoDataFrame(
        df, crs='EPSG:' + str(epsg),
        geometry=geoms
    )
    
    return gdata


def df_to_geodf(df, colGeom, epsg):
    """
    Regular Pandas Dataframe To GeoDataframe
    """
    
    from geopandas import GeoDataFrame
    
    return GeoDataFrame(
        df, crs='EPSG:{}'.format(epsg),
        geometry=colGeom
    )

def json_obj_to_geodf(json_obj, epsg):
    """
    Json Object to GeoDataFrame
    """
    
    from geopandas import GeoDataFrame
    
    return GeoDataFrame.from_features(
        json_obj['features'], 'EPSG:{}'.format(str(epsg))
    )

