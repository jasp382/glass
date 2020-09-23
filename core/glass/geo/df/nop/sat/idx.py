"""
Apply Indexes to highligh LULC types in Satellite Imagery

Use GDAL to apply index
"""


def ndwi2(green, nir, outRst, toReflectance=10000):
    """
    Apply Normalized Difference Water Index
    
    In Sentinel L2 Products, the raster value is the Reflectance
    multiplied by 10000, so to get the real reflectance, we have to apply:
    rst / 10000... toReflectance are the 10000 value in this example
    
    EXPRESSION: ((green / toReflectance) - (nir /toReflectance)) / 
    ((green / toReflectance) + (nir /toReflectance))
    """
    
    return outRst

def ndvi(nir, red, outRst):
    """
    Apply Normalized Difference NIR/Red Normalized Difference
    Vegetation Index, Calibrated NDVI - CDVI
    
    https://www.indexdatabase.de/db/i-single.php?id=58
    
    EXPRESSION: (nir - red) / (nir + red)
    """
    
    import numpy        as np
    from osgeo          import gdal, gdal_array
    from glass.dct.geo.torst import obj_to_rst
    
    # Open Images
    src_nir = gdal.Open(nir, gdal.GA_ReadOnly)
    src_red = gdal.Open(red, gdal.GA_ReadOnly)
    
    # To Array
    num_nir = src_nir.GetRasterBand(1).ReadAsArray().astype(float)
    num_red = src_red.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndvi = (num_nir - num_red) / (num_nir + num_red)
    
    # Place NoData Value
    nirNdVal = src_nir.GetRasterBand(1).GetNoDataValue()
    redNdVal = src_red.GetRasterBand(1).GetNoDataValue()
    
    ndNdvi = np.amin(ndvi) - 1
    
    np.place(ndvi, num_nir==nirNdVal, ndNdvi)
    np.place(ndvi, num_red==redNdVal, ndNdvi)
    
    # Export Result
    return obj_to_rst(ndvi, outRst, nir, noData=ndNdvi)


def nbr(nir, swir, outrst):
    """
    Normalized Burn Ratio
    
    EXPRESSION Sentinel-2A: (9-12) / (9+12)
    """
    
    import numpy        as np
    from osgeo          import gdal, gdal_array
    from glass.dct.geo.torst import obj_to_rst
    
    # Open Images
    srcNir  = gdal.Open(nir, gdal.GA_ReadOnly)
    srcSwir = gdal.Open(swir, gdal.GA_ReadOnly)
    
    # To Array
    numNir  = srcNir.GetRasterBand(1).ReadAsArray().astype(float)
    numSwir = srcSwir.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    nbr = (numNir - numSwir) / (numNir + numSwir)
    
    # Place NoData Value
    nirNdVal  = srcNir.GetRasterBand(1).GetNoDataValue()
    swirNdVal = srcSwir.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(nbr) - 1
    
    np.place(nbr, numNir == nirNdVal, nd)
    np.place(nbr, numSwir == swirNdVal, nd)
    
    # Export Result
    return obj_to_rst(nbr, outrst, nir, noData=nd)
