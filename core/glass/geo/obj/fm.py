"""
Data to GeoData
"""

import numpy as np

def imgsrc_to_num(img, flatten=None, with_nodata=True):
    """
    Convert Raster Source to Numpy Array
    """

    if not flatten and with_nodata:
        return img.ReadAsArray()
    elif flatten and with_nodata:
        return img.ReadAsArray().flatten()
    elif flatten and not with_nodata:
        bnd = img.GetRasterBand(1)
        no_val = bnd.GetNoDataValue()
        values = img.ReadAsArray().flatten()

        return np.delete(values, np.where(values==no_val), None)
    else:
        bnd = img.GetRasterBand(1)
        no_val = bnd.GetNoDataValue()
        values = img.ReadAsArray()

        return np.delete(values, np.where(values==no_val), None)

