"""
Raster to array
"""

import os
import numpy as np

from osgeo import gdal, gdal_array



def rst_to_array(r, flatten=False, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """

    from glass.rd.rsrc import imgsrc_to_num
    
    img = gdal.Open(r)

    return imgsrc_to_num(img, flatten=flatten, with_nodata=with_nodata)


def rst_to_geodf(in_rst):
    """
    Raster To GeoDataframe
    """

    import pandas       as pd
    from glass.pd.dagg  import dfcolstorows
    from glass.it.pd    import pnt_dfwxy_to_geodf
    from glass.prop.prj import rst_epsg
        
    src = gdal.Open(in_rst)
    num = src.ReadAsArray()
    ndval = src.GetRasterBand(1).GetNoDataValue()

    left, cellx, z, top, c, celly = src.GetGeoTransform()

    numdf = pd.DataFrame(num)
    numdf['idx'] = numdf.index

    res = dfcolstorows(numdf, 'col', 'val', colFid='idx')

    res = res[res.val != ndval]

    res['x'] = (left + (cellx / 2)) + (cellx * res.col)
    res['y'] = (top + (celly / 2)) + (celly * res.idx)

    res.drop(['col', 'idx'], axis=1, inplace=True)
    res.rename(columns={'val' : 'Value'}, inplace=True)

    geodf = pnt_dfwxy_to_geodf(res, 'x', 'y', rst_epsg(in_rst))

    return geodf


def array_to_geodf(np_arr, geo_params, epsg, ndval):
    """
    Array To GeoDataFrame
    """

    import pandas as pd
    from glass.pd.dagg import dfcolstorows
    from glass.it.pd   import pnt_dfwxy_to_geodf

    left, cellx, z, top, c, celly = geo_params

    numdf = pd.DataFrame(np_arr)
    numdf['idx'] = numdf.index

    res = dfcolstorows(numdf, 'col', 'val', colFid='idx')

    res = res[res.val != ndval]

    res['x'] = (left + (cellx / 2)) + (cellx * res.col)
    res['y'] = (top + (celly / 2)) + (celly * res.idx)

    res.drop(['col', 'idx'], axis=1, inplace=True)
    res.rename(columns={'val' : 'Value'}, inplace=True)

    geodf = pnt_dfwxy_to_geodf(res, 'x', 'y', epsg)

    return geodf


def rst_to_refarray(r, rshp=None, rmnd=True):
    """
    Read raster and convert it to an array to be used
    as Y in a Sklearn model
    """

    ysrc = gdal.Open(r, gdal.GA_ReadOnly)

    # Get NoData value
    nd_val = ysrc.GetRasterBand(1).GetNoDataValue()

    # Get real data
    ynum = ysrc.GetRasterBand(1).ReadAsArray()

    _rshp = (-1, 1) if not rshp else ynum.shape[0] * ynum.shape[1] \
        if rshp == 'flatten' else rshp
    
    ynum = ynum.reshape(_rshp)

    # Remove NoData Values
    y = ynum[ynum != nd_val] if rmnd else ynum

    # Get Shape
    shp = (ysrc.RasterYSize, ysrc.RasterXSize)

    return y, nd_val, shp


def rsts_to_featarray(imgvar):
    """
    Read Rasters to use them as features in a Sklearn 
    model
    """

    if type(imgvar) == str and os.path.isfile(imgvar):
        imgvar = [imgvar]
    
    elif type(imgvar) == str and not os.path.isfile(imgvar):
        raise ValueError('imgvar is not valid; it is a string but not an existing file')
    
    # Open feature images
    img_var = [gdal.Open(i, gdal.GA_ReadOnly) for i in imgvar]

    # Get band number of each raster
    img_bnd = [i.RasterCount for i in img_var]

    # Check images shape
    ref_shp = (img_var[0].RasterYSize, img_var[0].RasterXSize)
    if len(img_var) > 1:
        for r in range(1, len(img_var)):
            rst_shp = (img_var[r].RasterYSize, img_var[r].RasterXSize)

            if ref_shp != rst_shp:
                raise ValueError(
                    'There are at least two raster files with different shape'
                )
    
    # Get features number
    nvar = sum(img_bnd)

    # Convert feature images to array
    X = np.zeros(
        (ref_shp[0], ref_shp[1], nvar),
        gdal_array.GDALTypeCodeToNumericTypeCode(
            img_var[0].GetRasterBand(1).DataType
        )
    )

    f = 0
    for r in range(len(img_var)):
        for b in range(img_bnd[r]):
            X[:, :, f] = img_var[r].GetRasterBand(b + 1).ReadAsArray()

            f += 1
    
    # Reshape
    nshp = (X.shape[0] * X.shape[1], X.shape[2])
    n_x = X[:, :, :nvar].reshape(nshp)

    return X, n_x

