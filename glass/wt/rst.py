"""
Data to Raster File
"""

import numpy as np
from osgeo import gdal, gdal_array

from glass.prop.df import drv_name

"""
Array to Raster
"""

def obj_to_rst(inArray, outRst, geotrans, epsg, noData=None):
    """
    Send Array to Raster

    inArray - array of array with raster date
    outRst - path to output raster file - 
        inArray will be written in this file
    """

    from glass.prop.rst import compress_option
    from glass.prop.prj import epsg_to_wkt
    
    rows, cols = inArray.shape
    drv_n      = drv_name(outRst)
    driver     = gdal.GetDriverByName(drv_n)

    c_opt = compress_option(drv_n)
    if c_opt:
        out = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype),
            options=[c_opt]
        )
    else:
        out = driver.Create(
            outRst, cols, rows, 1,
            gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype)
        )
    
    out.SetGeoTransform(geotrans)

    outBand = out.GetRasterBand(1)
    
    if noData or noData==0:
        outBand.SetNoDataValue(noData)
        
    outBand.WriteArray(inArray)
    
    out.SetProjection(epsg_to_wkt(epsg))
    
    outBand.FlushCache()
    
    return outRst


def rst_from_origin(topleft, shape, cellsize, rst, epsg):
    """
    Create Raster with a certain origin, shape and cellsize
    """

    # GeoTransform Parameters
    left, top = topleft
    nrows, ncols = shape
    cellx, celly = cellsize

    res = np.ones((nrows, ncols))

    # Export
    gtrans = (left, cellx, 0, top, 0, celly)

    obj_to_rst(res, rst, gtrans, epsg)

    return rst

