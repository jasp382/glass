"""
Read Raster Data using ARCGIS PRO
"""

import numpy as np
import arcpy


def rst_to_array(r, flatten=None, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """
    
    img_array = arcpy.RasterToNumPyArray(r)

    if not with_nodata:
        rst = arcpy.Raster(r)
        nd = rst.noDataValue

        whr = np.where(img_array==nd)
    else:
        nd, whr = None, None
    
    if not flatten and with_nodata:
        return img_array
    
    elif flatten and with_nodata:
        return img_array.flatten()
    
    elif flatten and not with_nodata:
        values = img_array.flatten()
        cval = np.delete(values, whr, None)

        return cval
    else:
        return np.delete(img_array, whr, None)
    

def ag_rst_to_refarray(rst, rshp=None, rmnd=True):
    """
    Read raster and convert it to an array to be used
    as Y in a Sklearn model
    """

    desc = arcpy.Describe(rst)

    # Get NoData value
    nd_val = desc.noDataValue

    # Get real data
    ynum = arcpy.RasterToNumPyArray(rst)

    _rshp = (-1, 1) if not rshp else ynum.shape[0] * ynum.shape[1] \
        if rshp == 'flatten' else rshp
    
    ynum = ynum.reshape(_rshp)

    # Remove NoData Values
    y = ynum[ynum != nd_val] if rmnd else ynum

    # Get Original raster Shape
    shp = (int(desc.height), int(desc.width))

    return y, nd_val, shp



def rst_to_lyr(r, lyrname=None):
    """
    Raster Dataset to Raster Layer
    """

    from glass.pys.oss import fprop

    n = fprop(r, 'fn') if not lyrname or \
        type(lyrname) != str else lyrname
    
    lyr = arcpy.MakeRasterLayer_management(r, n, "", "", "1")
    
    return n

