"""
Get representative Sentinel-2 images for each month
"""

import os

from glass.pys.oss import lst_fld, lst_ff
from glass.rst.sat.fusion import month_median


if __name__ ==  "__main__":
    fld = '/mnt/c/s2_vflores21'

    file_format = '.tif'

    ref = '/mnt/c/stdrst_valeflores.tif'

    month_median(
        fld, ref, fld,
        fformat=file_format
    )

