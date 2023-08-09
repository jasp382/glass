"""
Play with GeoDataFrames
"""

import pandas as pd
from geopandas import GeoDataFrame

def pnt_dfwxy_to_geodf(df, colX, colY, epsg):
    """
    Pandas Dataframe with numeric x, y columns
    to GeoDataframe
    
    Works Only for Points
    """
    
    from shapely.geometry import Point
    
    geoms = [Point(xy) for xy in zip(df[colX], df[colY])]
    df.drop([colX, colY], axis=1, inplace=True)
    gdata = GeoDataFrame(
        df, crs=f'EPSG:{str(epsg)}',
        geometry=geoms
    )
    
    return gdata


def df_to_geodf(df, colGeom, epsg, cols=None):
    """
    Regular Pandas Dataframe To GeoDataframe
    """
    
    return GeoDataFrame(
        df, columns=cols,
        crs=f'EPSG:{epsg}', geometry=colGeom
    )


def obj_to_geodf(obj, geom, epsg, cols=None):
    """
    Array or dict to GeoDataFrame

    Assuming geometry is a wkt
    """

    from shapely import wkt

    df = pd.DataFrame(obj, columns=cols)

    df[geom] = df[geom].apply(wkt.loads)

    return df_to_geodf(df, geom, epsg, cols=None)


def json_obj_to_geodf(json_obj, epsg):
    """
    Json Object to GeoDataFrame
    """
    
    return GeoDataFrame.from_features(
        json_obj['features'], f'EPSG:{str(epsg)}'
    )
