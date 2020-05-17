"""
Extent related
"""


def get_ext(inFile, outEpsg=None):
    """
    Get Extent of any GIS Data
    
    return None if inFile is not a GIS File
    """
    
    from glass.geo.prop.df import check_isRaster, check_isShp
    
    if check_isRaster(inFile):
        from glass.geo.prop.rst import rst_ext
        
        extent = rst_ext(inFile)
    
    else:
        if check_isShp(inFile):
            from glass.geo.prop.feat import get_ext as gext
            
            extent = gext(inFile)
        
        else:
            return None
    
    if outEpsg:
        from glass.geo.prop.prj import get_epsg
        
        fileEpsg = get_epsg(inFile)
        
        if not fileEpsg:
            raise ValueError('cannot get EPSG of input file')
        
        if fileEpsg != outEpsg:
            from glass.geo.obj.g   import new_pnt
            from glass.geo.obj.prj import prj_ogrgeom
            
            bt_left = prj_ogrgeom(new_pnt(
                extent[0], extent[2]), fileEpsg, outEpsg)
            top_right = prj_ogrgeom(new_pnt(
                extent[1], extent[3]), fileEpsg, outEpsg)
            
            left , bottom = bt_left.GetX(), bt_left.GetY()
            right, top    = top_right.GetX(), top_right.GetY()
            
            extent = [left, right, bottom, top]
    
    return extent

