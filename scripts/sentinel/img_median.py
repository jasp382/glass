"""
Get representative Sentinel-2 images for each month
"""

from glass.rst.sat.fusion import month_median


if __name__ ==  "__main__":
    fld = '/home/jasp/autocls/s2_vflores21'

    file_format = '.tif'

    ref = '/mnt/x/autocls_e4/stdreg/stdrst_valeflores.tif'

    month_median(
        fld, ref, fld,
        fformat=file_format
    )

