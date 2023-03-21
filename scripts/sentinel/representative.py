"""
Get representative Sentinel-2 images for each month
"""

import os

from glass.pys.oss import lst_fld, lst_ff
from glass.rst.sat.fusion import month_representative


if __name__ ==  "__main__":
    fld = '/mnt/disk1/jasp/a2autocls2023/imgcmb/rmp2018'

    file_format = '.tif'

    ofolder = '/mnt/disk1/jasp/a2autocls2023/imgcmb/best2018'

    # List folders
    folders = lst_fld(fld)

    # Get reference image for each folder
    fld_ref = {}
    for f in folders:
        bf = lst_ff(f, file_format=file_format, rfilename=True)

        for b in bf:
            if 'B02_10m' in b:
                fld_ref[f] = os.path.join(f, b)
                break
    
    # Get representative image
    for f in fld_ref:
        month_representative(
            f, fld_ref[f], ofolder,
            os.path.basename(f),
            fformat=file_format
        )

