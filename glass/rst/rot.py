"""
Raster rotation related
"""

from osgeo import gdal


def rst_rotation(inFolder, template, outFolder, img_format='.tif'):
    """
    Invert raster data
    """
    
    import os
    from glass.pys.oss  import lst_ff
    from glass.rd.rsrc  import imgsrc_to_num
    from glass.prop.img import get_nd, rst_epsg
    from glass.wt.rst   import obj_to_rst
    
    rasters = lst_ff(inFolder, file_format=img_format)
    
    for rst in rasters:
        src = gdal.Open(rst, gdal.GA_ReadOnly)
        a   = imgsrc_to_num(src)
        nd  = get_nd(src)
        
        obj_to_rst(a[::-1],
            os.path.join(outFolder, os.path.basename(rst)),
            src.GetGeoTransform(), rst_epsg(src), noData=nd
        )
    
    return outFolder

