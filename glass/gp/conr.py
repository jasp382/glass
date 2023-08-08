"""
Geometry conversion/change operations
"""


def orig_dest_to_polyline(srcPoints, srcField, 
                          destPoints, destField, outShp):
    """
    Connect origins to destinations with a polyline which
    length is the minimum distance between the origin related
    with a specific destination.
    
    One origin should be related with one destination.
    These relations should be expressed in srcField and destField
    """
    
    from geopandas        import GeoDataFrame
    from shapely.geometry import LineString
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import df_to_shp
    
    srcPnt = shp_to_obj(srcPoints)
    desPnt = shp_to_obj(destPoints)
    
    joinDf = srcPnt.merge(
        desPnt, how='inner',
        left_on=srcField, right_on=destField
    )
    
    joinDf["geometry"] = joinDf.apply(
        lambda x: LineString(
            x["geometry_x"], x["geometry_y"]
        ), axis=1
    )
    
    joinDf.drop(["geometry_x", "geometry_y"], axis=1, inplace=True)
    
    a = GeoDataFrame(joinDf)
    
    df_to_shp(joinDf, outShp)
    
    return outShp

