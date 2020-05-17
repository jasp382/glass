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
    
    from glass.dct              import tbl_to_obj
    from glass.dct.geo.toshp    import df_to_shp
    from glass.geo.obj.gop.prox import df_buffer_extent
    from glass.geo.prop.prj     import get_epsg_shp
    
    inDf = tbl_to_obj(inShp)

    epsg = get_epsg_shp(inShp) if not inEpsg else inEpsg
    
    result = df_buffer_extent(inDf, epsg, meterTolerance)
    
    return df_to_shp(result, outShp)
