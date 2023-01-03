"""
Extent related
"""


def get_ext(inFile, outEpsg=None):
    """
    Get Extent of any GIS Data
    
    return None if inFile is not a GIS File
    """
    
    from glass.prop import is_rst, is_shp
    
    if is_rst(inFile):
        from glass.prop.rst import rst_ext
        
        extent = rst_ext(inFile)
    
    else:
        if is_shp(inFile):
            from glass.prop.feat import get_ext as gext
            
            extent = gext(inFile)
        
        else:
            return None
    
    if outEpsg:
        from glass.prop.prj import get_epsg
        
        fileEpsg = get_epsg(inFile)
        
        if not fileEpsg:
            raise ValueError('cannot get EPSG of input file')
        
        if fileEpsg != outEpsg:
            from glass.gobj    import new_pnt
            from glass.prj.obj import prj_ogrgeom
            
            bt_left = prj_ogrgeom(new_pnt(
                extent[0], extent[2]), fileEpsg, outEpsg,
                api='ogr' if outEpsg != 4326 else 'shapely'
            )
            top_right = prj_ogrgeom(new_pnt(
                extent[1], extent[3]), fileEpsg, outEpsg,
                api='ogr' if outEpsg != 4326 else 'shapely'
            )
            
            left , bottom = bt_left.GetX(), bt_left.GetY()
            right, top    = top_right.GetX(), top_right.GetY()
            
            extent = [left, right, bottom, top]
    
    return extent



"""
GeoPandas Related
"""

def featext_to_dfcols(df, geomCol):
    """
    Add minx, miny, maxx, maxy to dataframe
    """
    
    return df.merge(
        df[geomCol].bounds, how='inner',
        left_index=True, right_index=True
    )


def get_dfext(df, geomCol):
    """
    Add minx, miny, maxx, maxy to dataframe
    """

    ndf = featext_to_dfcols(df, geomCol)

    return [
        # left, right
        ndf.minx.min(), ndf.maxx.max(),
        # Bottom, top
        ndf.miny.min(), ndf.maxy.max()
    ]

