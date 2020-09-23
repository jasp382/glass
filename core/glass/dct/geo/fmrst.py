"""
Raster to array
"""


def rst_to_array(r, flatten=False, with_nodata=True):
    """
    Convert Raster image to numpy array
    
    If flatten equal a True, the output will have a shape of (1, 1).
    
    If with_nodata equal a True, the output will have the nodata values
    """
    
    from osgeo     import gdal
    from glass.geo.obj.fm import imgsrc_to_num
    
    img = gdal.Open(r)

    return imgsrc_to_num(img, flatten=flatten, with_nodata=with_nodata)


def rst_to_geodf(in_rst):
    """
    Raster To GeoDataframe
    """

    from osgeo import gdal
    import numpy as np
    import pandas as pd
    from glass.dp.pd.dagg   import dfcolstorows
    from glass.geo.obj.pd   import pnt_dfwxy_to_geodf
    from glass.geo.prop.prj import get_rst_epsg
        
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

    geodf = pnt_dfwxy_to_geodf(res, 'x', 'y', get_rst_epsg(in_rst))

    return geodf


def array_to_geodf(np_arr, geo_params, epsg, ndval):
    """
    Array To GeoDataFrame
    """

    from osgeo import gdal
    import numpy as np
    import pandas as pd
    from glass.dp.pd.dagg import dfcolstorows
    from glass.geo.obj.pd import pnt_dfwxy_to_geodf

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

