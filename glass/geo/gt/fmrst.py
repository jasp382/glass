"""
Raster to array
"""


def rst_to_array(r, flatten=False, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """
    
    from osgeo     import gdal
    from glass.geo.gm.fm import imgsrc_to_num
    
    img = gdal.Open(r)

    return imgsrc_to_num(img, flatten=flatten, with_nodata=with_nodata)

