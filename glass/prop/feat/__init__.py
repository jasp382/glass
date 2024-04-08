"""
Feature Classes Properties
"""


"""
Geometric Properties
"""

def get_cntr_bnd(shp, isFile=None):
    """
    Return centroid (OGR Point object) of a Boundary (layer with a single
    feature).
    """
    
    from osgeo         import ogr
    from glass.prop.df import drv_name
    
    if isFile:
        shp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = shp.GetLayer()
    
        feat = lyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = shp
    
    centroid = geom.Centroid()
    
    cnt = ogr.CreateGeometryFromWkt(centroid.ExportToWkt())
    
    shp.Destroy()
    
    return cnt

