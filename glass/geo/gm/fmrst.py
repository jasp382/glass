"""
From Raster to Something
"""

def rst_to_geodf(in_rst):
    """
    Raster To GeoDataframe
    """

    from osgeo import gdal
    import numpy as np
    import pandas as pd
    from glass.pyt.df.mng  import dfcolstorows
    from glass.geo.gm.to   import pnt_dfwxy_to_geodf
    from glass.geo.gt.prop.prj import get_rst_epsg
        
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
    from glass.pyt.df.mng import dfcolstorows
    from glass.geo.gm.to  import pnt_dfwxy_to_geodf

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

