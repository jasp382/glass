"""
Data to Raster File
"""

from osgeo         import gdal, osr, gdal_array
from glass.prop.df import drv_name

"""
Array to Raster
"""

def obj_to_rst(inArray, outRst, template, noData=None, geotrans=None):
    """
    Send Array to Raster

    inArray - array of array with raster date
    outRst - path to output raster file - 
        inArray will be written in this file
    """
    
    from glass.prop.rst import compress_option

    if type(template).__name__ == 'Dataset':
        img_template = template
    else:
        img_template  = gdal.Open(template)
        
    geo_transform = img_template.GetGeoTransform() if not geotrans else \
        geotrans
    rows, cols    = inArray.shape
    drv_n         = drv_name(outRst)
    driver        = gdal.GetDriverByName(drv_n)

    c_opt = compress_option(drv_n)
    if c_opt:
        out       = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype),
            options=[c_opt]
        )
    else:
        out       = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype)
        )
    out.SetGeoTransform(geo_transform)
    outBand       = out.GetRasterBand(1)
    
    if noData or noData==0:
        outBand.SetNoDataValue(noData)
        
    outBand.WriteArray(inArray)
        
    proj = osr.SpatialReference(wkt=img_template.GetProjection())
    
    if proj:
        out.SetProjection(img_template.GetProjection())
    
    outBand.FlushCache()
    
    return outRst

