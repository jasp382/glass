"""
Buffering Tools
"""

"""
Buffers based on extent
"""

def buffer_ext(inShp, meterTolerance, outShp, inEpsg=None):
    """
    For all geometries, calculate the boundary given by 
    the sum between the feature extent and the Tolerance variable
    """
    
    from glass.dct.fm          import tbl_to_obj
    from glass.geo.gt.toshp    import df_to_shp
    from glass.geo.gm.gop.prox import df_buffer_extent
    from glass.geo.gt.prop.prj import get_epsg_shp
    
    inDf = tbl_to_obj(inShp)

    epsg = get_epsg_shp(inShp) if not inEpsg else inEpsg
    
    result = df_buffer_extent(inDf, epsg, meterTolerance)
    
    return df_to_shp(result, outShp)
