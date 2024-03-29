"""
Extent related
"""

import os


def get_ext(ingeo, oepsg=None, geolyr=None):
    """
    Get Extent of any GIS Data
    
    return None if inFile is not a GIS File
    """
    
    from glass.prop.df import is_rst, is_shp

    ishp, irst = is_shp(ingeo), is_rst(ingeo)
    
    if irst and not ishp:
        from glass.prop.rst import rst_ext as gext

        isrc = ingeo
    
    elif not irst and ishp:
        from glass.prop.shp import get_ext as gext

        isrc = ingeo
        
    else:
        # Probabily, we have a geodatabase
        if '.gdb' in ingeo and not geolyr:
            from glass.prop.shp import get_ext as gext

            isrc  = os.path.dirname(ingeo)
            geolyr = os.path.basename(ingeo)

            if isrc[-4:] != '.gdb':
                isrc = os.path.dirname(isrc)
            
            ishp = True
        
        else: return None
    
    ext = gext(isrc) if not ishp else \
        gext(isrc, lyrname=geolyr)
    
    if oepsg:
        from glass.prop.prj import get_epsg
        
        iepsg = get_epsg(isrc, lyrname=geolyr)
        
        if not iepsg:
            raise ValueError('cannot get EPSG of input file')
        
        if iepsg != oepsg:
            from glass.gobj    import new_pnt
            from glass.prj.obj import prj_ogrgeom
            
            bt_left = prj_ogrgeom(new_pnt(
                ext[0], ext[2]), iepsg, oepsg,
                api='ogr' if oepsg != 4326 else 'shapely'
            )
            top_right = prj_ogrgeom(new_pnt(
                ext[1], ext[3]), iepsg, oepsg,
                api='ogr' if oepsg != 4326 else 'shapely'
            )
            
            left , bottom = bt_left.GetX(), bt_left.GetY()
            right, top    = top_right.GetX(), top_right.GetY()
            
            ext = [left, right, bottom, top]
    
    return ext



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

