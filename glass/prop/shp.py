"""
Feature Class properties
"""

"""
Extent of Shapefiles and such
"""


def get_ext(shp, lyrname=None):
    """
    Return extent of a Vectorial file
    
    Return a tuple object with the follow order:
    (left, right, bottom, top)
    
    API'S Available:
    * ogr;
    """
    
    gisApi = 'ogr'
    
    if gisApi == 'ogr':
        from osgeo         import ogr
        from glass.prop.df import drv_name

        drv = 'OpenFileGDB' if '.gdb' in shp else drv_name(shp)
    
        dt = ogr.GetDriverByName(drv).Open(shp, 0)

        lyr = dt.GetLayer(lyrname) if lyrname else dt.GetLayer()
        
        extent = lyr.GetExtent()
    
        dt.Destroy()
    
    return list(extent)

