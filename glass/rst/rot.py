"""
Raster rotation related
"""

def rst_rotation(inFolder, template, outFolder, img_format='.tif'):
    """
    Invert raster data
    """
    
    import os; from osgeo import gdal
    from glass.pys.oss    import lst_ff
    from glass.rd.rst   import rst_to_array
    from glass.prop.rst import get_nodata
    from glass.wt.rst   import obj_to_rst
    
    rasters = lst_ff(inFolder, file_format=img_format)
    
    for rst in rasters:
        a  = rst_to_array(rst)
        nd = get_nodata(rst)
        
        obj_to_rst(a[::-1],
            os.path.join(outFolder, os.path.basename(rst)),
            template, noData=nd
        )
    
    return outFolder

