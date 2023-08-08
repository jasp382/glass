"""
Apply Indexes to highligh LULC types in Satellite Imagery

Use GDAL to apply index
"""

import numpy      as np
from osgeo        import gdal
from glass.wt.rst import obj_to_rst


def calc_ndwi(green, nir_swir, outRst):
    """
    Apply Normalized Difference Water Index
    
    In Sentinel L2 Products, the raster value is the Reflectance
    multiplied by 10000, so to get the real reflectance, we have to apply:
    rst / 10000... toReflectance are the 10000 value in this example
    
    EXPRESSION: ((green / toReflectance) - (nir /toReflectance)) / 
    ((green / toReflectance) + (nir /toReflectance))
    """

    api = 'gdal'
    nir = nir_swir

    if api == 'gdal':
        srcg   = gdal.Open(green, gdal.GA_ReadOnly)
        srcnir = gdal.Open(nir, gdal.GA_ReadOnly)

        # To Array
        num_green = srcg.GetRasterBand(1).ReadAsArray().astype(float)
        num_nir   = srcnir.GetRasterBand(1).ReadAsArray().astype(float)

        # Calculation
        ndwir = (num_green - num_nir) / (num_green + num_nir)

        # Place NoData Value
        gnd = srcg.GetRasterBand(1).GetNoDataValue()
        nnd = srcnir.GetRasterBand(1).GetNoDataValue()

        nd = np.amin(ndwir) - 1

        np.place(ndwir, num_green==gnd, nd)
        np.place(ndwir, num_nir==nnd, nd)
    
        # Export Result
        outrst = obj_to_rst(ndwir, outRst, nir, noData=nd)
    
    else:
        raise ValueError(f'Sorry, API {api} is not available')
    
    return outrst


def calc_ndvi(nir, red, outRst):
    """
    Apply Normalized Difference NIR/Red Normalized Difference
    Vegetation Index, Calibrated NDVI - CDVI
    
    https://www.indexdatabase.de/db/i-single.php?id=58
    
    EXPRESSION: (nir - red) / (nir + red)
    """
    
    # Open Images
    src_nir = gdal.Open(nir, gdal.GA_ReadOnly)
    src_red = gdal.Open(red, gdal.GA_ReadOnly)
    
    # To Array
    num_nir = src_nir.GetRasterBand(1).ReadAsArray().astype(float)
    num_red = src_red.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndvir = (num_nir - num_red) / (num_nir + num_red)
    
    # Place NoData Value
    nirNdVal = src_nir.GetRasterBand(1).GetNoDataValue()
    redNdVal = src_red.GetRasterBand(1).GetNoDataValue()
    
    ndNdvi = np.amin(ndvir) - 1
    
    np.place(ndvir, num_nir==nirNdVal, ndNdvi)
    np.place(ndvir, num_red==redNdVal, ndNdvi)
    
    # Export Result
    return obj_to_rst(ndvir, outRst, nir, noData=ndNdvi)


def calc_nbr(nir, swir, outrst):
    """
    Normalized Burn Ratio
    
    EXPRESSION Sentinel-2A: (9-12) / (9+12)
    """
    
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


def calc_savi(nir, red, out):
    """
    Apply Soil Adjusted Vegetation
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sred = gdal.Open(red, gdal.GA_ReadOnly)

    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    savi = (1.5 * (nnir - nred)) / (nnir + nred + 0.5)

    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    red_nd = sred.GetRasterBand(1).GetNoDataValue()
    
    savi_nd = np.amin(savi) - 1
    
    np.place(savi, nnir==nir_nd, savi_nd)
    np.place(savi, nred==red_nd, savi_nd)
    
    # Export Result
    return obj_to_rst(savi, out, nir, noData=savi_nd)


def calc_evi(nir, red, blue, out):
    """
    Apply Enhanced Vegetation Index
    """

    d = {'n' : nir, 'r' : red, 'b' : blue}

    # Open Images
    src = {k: gdal.Open(d[k], gdal.GA_ReadOnly) for k in d}

    # To Array
    num = {k: src[k].GetRasterBand(
        1).ReadAsArray().astype(float) for k in d}

    # Do calculation
    deno = (num['n'] + 6.0 * num['r'] - 7.5 * num['b']) + 1.0
    evi = np.where(
        deno == 0, -1,
        2.5 * ((num['n'] - num['r']) / deno)
    )

    # Place NoData Value
    evi_nd = np.amin(evi) - 1

    for k in d:
        nd = src[k].GetRasterBand(1).GetNoDataValue()

        np.place(evi, num[k]==nd, evi_nd)
    
    np.place(evi, deno == 0, evi_nd)
    np.place(evi, evi < -1, -1)
    np.place(evi, evi > 1, 1)
    
    # Export Result
    return obj_to_rst(evi, out, nir, noData=evi_nd)


def calc_ndre(nir, re, out):
    """
    Apply Normalized Difference Red Edge
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sre  = gdal.Open(re, gdal.GA_ReadOnly)
    
    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nre  = sre.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndre = (nnir - nre) / (nnir + nre)
    
    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    re_nd  = sre.GetRasterBand(1).GetNoDataValue()
    
    ndre_nd = np.amin(ndre) - 1
    
    np.place(ndre, nnir==nir_nd, ndre_nd)
    np.place(ndre, nre==re_nd, ndre_nd)
    
    # Export Result
    return obj_to_rst(ndre, out, nir, noData=ndre_nd)


def calc_ngrdi(green, red, out):
    """
    Apply Normalized Green/Red Vegetation Index
    """

    # Open Images
    sgre = gdal.Open(green, gdal.GA_ReadOnly)
    sred = gdal.Open(red, gdal.GA_ReadOnly)
    
    # To Array
    ngre = sgre.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ngrdi = (ngre - nred) / (ngre + nred)
    
    # Place NoData Value
    green_nd = sgre.GetRasterBand(1).GetNoDataValue()
    red_nd   = sred.GetRasterBand(1).GetNoDataValue()
    
    ngrdi_nd = np.amin(ngrdi) - 1
    
    np.place(ngrdi, ngre==green_nd, ngrdi_nd)
    np.place(ngrdi, nred==red_nd, ngrdi_nd)
    
    # Export Result
    return obj_to_rst(ngrdi, out, green, noData=ngrdi_nd)


def calc_ndbi(swir, nir, out):
    """
    Apply Normalized Difference Build Index
    """

    # Open Images
    sswir = gdal.Open(swir, gdal.GA_ReadOnly)
    snir  = gdal.Open(nir, gdal.GA_ReadOnly)
    
    # To Array
    nswir = sswir.GetRasterBand(1).ReadAsArray().astype(float)
    nnir  = snir.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndbi = (nswir - nnir) / (nswir + nnir)
    
    # Place NoData Value
    swir_nd = sswir.GetRasterBand(1).GetNoDataValue()
    nir_nd  = snir.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndbi) - 1
    
    np.place(ndbi, nswir==swir_nd, nd)
    np.place(ndbi, nnir==nir_nd, nd)
    
    # Export Result
    return obj_to_rst(ndbi, out, swir, noData=nd)


def calc_ndsi(swir2, blue, out):
    """
    Apply Normalized Difference Soil Index
    """

    # Open Images
    sswir = gdal.Open(swir2, gdal.GA_ReadOnly)
    sblue = gdal.Open(blue, gdal.GA_ReadOnly)
    
    # To Array
    nswir = sswir.GetRasterBand(1).ReadAsArray().astype(float)
    nblue = sblue.GetRasterBand(1).ReadAsArray().astype(float)
    
    # Do Calculation
    ndsi = (nswir - nblue) / (nswir + nblue)
    
    # Place NoData Value
    swir_nd = sswir.GetRasterBand(1).GetNoDataValue()
    blue_nd = sblue.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndsi) - 1
    
    np.place(ndsi, nswir==swir_nd, nd)
    np.place(ndsi, nblue==blue_nd, nd)
    
    # Export Result
    return obj_to_rst(ndsi, out, swir2, noData=nd)

