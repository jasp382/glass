"""
Apply Indexes to highligh LULC types in Satellite Imagery

Use GDAL to apply index
"""

import numpy      as np
from osgeo        import gdal

from glass.prop.img import rst_epsg
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

    api, nir = 'gdal', nir_swir

    if api == 'gdal':
        srcg   = gdal.Open(green, gdal.GA_ReadOnly)
        srcnir = gdal.Open(nir, gdal.GA_ReadOnly)

        # To Array
        num_green = srcg.GetRasterBand(1).ReadAsArray().astype(float)
        num_nir   = srcnir.GetRasterBand(1).ReadAsArray().astype(float)

        # Calculation
        den = num_green + num_nir
        ndwir = np.where(
            den == 0, 100,
            (num_green - num_nir) / den
        )

        # Place NoData Value
        gnd = srcg.GetRasterBand(1).GetNoDataValue()
        nnd = srcnir.GetRasterBand(1).GetNoDataValue()

        nd = np.amin(ndwir) - 1

        np.place(ndwir, num_green == 0, nd)
        np.place(ndwir, num_nir == 0, nd)

        np.place(ndwir, num_green==gnd, nd)
        np.place(ndwir, num_nir==nnd, nd)
    
        # Export Result
        outrst = obj_to_rst(
            ndwir, outRst, srcg.GetGeoTransform(),
            rst_epsg(srcg), noData=nd
        )
    
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
    den = (num_nir + num_red)
    ndvir = np.where(
        den == 0, 100,
        (num_nir - num_red) / den
    )
    
    # Place NoData Value
    nirNdVal = src_nir.GetRasterBand(1).GetNoDataValue()
    redNdVal = src_red.GetRasterBand(1).GetNoDataValue()
    
    ndNdvi = np.amin(ndvir) - 1

    np.place(ndvir, num_nir == 0, ndNdvi)
    np.place(ndvir, num_red == 0, ndNdvi)
    
    np.place(ndvir, num_nir==nirNdVal, ndNdvi)
    np.place(ndvir, num_red==redNdVal, ndNdvi)
    
    # Export Result
    return obj_to_rst(
        ndvir, outRst, src_nir.GetGeoTransform(),
        rst_epsg(src_nir), noData=ndNdvi
    )


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
    return obj_to_rst(
        nbr, outrst, srcNir.GetGeoTransform(),
        rst_epsg(srcNir), noData=nd
    )


def calc_savi(nir, red, out, formula='regular'):
    """
    Apply Soil Adjusted Vegetation

    * regular - https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=87
    * adjusted - https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=209
    * modified
    """

    opt = ['regular', 'adjusted', 'modified']

    formula = 'regular' if formula not in opt else formula

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sred = gdal.Open(red, gdal.GA_ReadOnly)

    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    L = 0.5 # L varies from -0,9 and 1,6
    if formula == 'regular':
        savi = ((nnir - nred) / (nnir + nred + 0.5)) * (1 + L)
    
    elif formula == 'adjusted':
        n = nnir - 1.22 * nred - 0.03
        d = 1.22 * nnir + nred - 1.22 * 0.03 + 0.08 * (1 + 1.22**2)

        savi = 1.22 * (n/d)
    
    elif formula == 'modified':
        n = np.power(2 * nnir + 1, 2) - 8 * (nnir - nred)
        nsqrt = np.sqrt(n)

        savi = (2 * nnir + 1 - nsqrt) / 2

    # Place NoData Value
    nir_nd = snir.GetRasterBand(1).GetNoDataValue()
    red_nd = sred.GetRasterBand(1).GetNoDataValue()
    
    savi_nd = np.amin(savi) - 1
    
    np.place(savi, nnir==0, savi_nd)
    np.place(savi, nred==0, savi_nd)

    np.place(savi, nnir==nir_nd, savi_nd)
    np.place(savi, nred==red_nd, savi_nd)
    
    # Export Result
    return obj_to_rst(
        savi, out, nir, snir.GetGeoTransform(),
        rst_epsg(snir), noData=savi_nd
    )




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
    return obj_to_rst(
        evi, out, src['n'].GetGeoTransform(),
        rst_epsg(src['n']), noData=evi_nd
    )


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
    return obj_to_rst(
        ndre, out, snir.GetGeoTransform(),
        rst_epsg(snir), noData=ndre_nd
    )


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
    return obj_to_rst(
        ngrdi, out, sgre.GetGeoTransform(),
        rst_epsg(sgre), noData=ngrdi_nd
    )


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
    den = nswir + nnir
    ndbi = np.where(
        den == 0, 100,
        (nswir - nnir) / den
    )
    
    # Place NoData Value
    swir_nd = sswir.GetRasterBand(1).GetNoDataValue()
    nir_nd  = snir.GetRasterBand(1).GetNoDataValue()
    
    nd = np.amin(ndbi) - 1

    np.place(ndbi, nswir == 0, nd)
    np.place(ndbi, nnir == 0, nd)
    
    np.place(ndbi, nswir==swir_nd, nd)
    np.place(ndbi, nnir==nir_nd, nd)
    
    # Export Result
    return obj_to_rst(
        ndbi, out, sswir.GetGeoTransform(),
        rst_epsg(sswir), noData=nd
    )


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
    return obj_to_rst(
        ndsi, out, sswir.GetGeoTransform(),
        rst_epsg(sswir), noData=nd
    )


def calc_ci_rededge(nir, rededge, out):
    """
    Calculate Chlorophyll IndexRedEdge

    https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=131
    """

    # Open Images
    snir = gdal.Open(nir, gdal.GA_ReadOnly)
    sred = gdal.Open(rededge, gdal.GA_ReadOnly)
    
    # To Array
    nnir = snir.GetRasterBand(1).ReadAsArray().astype(float)
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    cire = np.where(
        nred == 0, 100,
        (nnir / nred) - 1
    )

    # Place NoData Value
    nd_nir = snir.GetRasterBand(1).GetNoDataValue()
    nd_red = sred.GetRasterBand(1).GetNoDataValue()

    nd_cire = np.amin(cire) - 1

    np.place(cire, nnir==0, nd_cire)
    np.place(cire, nred==0, nd_cire)

    np.place(cire, nnir==nd_nir, nd_cire)
    np.place(cire, nred==nd_red, nd_cire)

    # Export Result
    return obj_to_rst(
        cire, out, snir.GetGeoTransform(),
        rst_epsg(snir), noData=nd_cire
    )


def calc_coloration_idx(red, blue, out):
    """
    Calculate Coloration Index

    https://www.indexdatabase.de/db/si-single.php?sensor_id=96&rsindex_id=11
    """

    # Open Images
    sred  = gdal.Open(red, gdal.GA_ReadOnly)
    sblue = gdal.Open(blue, gdal.GA_ReadOnly)

    # To Array
    nred = sred.GetRasterBand(1).ReadAsArray().astype(float)
    nblue = sblue.GetRasterBand(1).ReadAsArray().astype(float)

    # Do calculation
    ci = np.where(nred == 0, 100, (nred - nblue) / nred)

    # Place NoData Value
    nd_red  = sred.GetRasterBand(1).GetNoDataValue()
    nd_blue = sblue.GetRasterBand(1).GetNoDataValue()

    nd_ci = np.amin(ci) - 1

    np.place(ci, nred==0, nd_ci)
    np.place(ci, nblue==0, nd_ci)

    np.place(ci, nred==nd_red, nd_ci)
    np.place(ci, nblue==nd_blue, nd_ci)

    return obj_to_rst(
        ci, out, sred.GetGeoTransform(),
        rst_epsg(sred), noData=nd_ci
    )

