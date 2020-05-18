"""
Numeric Operations

Aka Operations with Raster
"""

def rst_rotation(inFolder, template, outFolder, img_format='.tif'):
    """
    Invert raster data
    """
    
    import os; from osgeo import gdal
    from glass.pyt.oss     import lst_ff
    from glass.geo.gt.fmrst    import rst_to_array
    from glass.geo.gt.prop.rst import get_nodata
    from glass.geo.gt.torst    import obj_to_rst
    
    rasters = lst_ff(inFolder, file_format=img_format)
    
    for rst in rasters:
        a  = rst_to_array(rst)
        nd = get_nodata(rst)
        
        obj_to_rst(a[::-1],
            os.path.join(outFolder, os.path.basename(rst)),
            template, noData=nd
        )

