"""
Get representative Sentinel-2 images for each month
"""

import os

from glass.pys.oss import lst_fld, lst_ff
from glass.rst.sat.fusion import month_representative


if __name__ ==  "__main__":
    fld = '/home/jasp/autocls/imgmonth20'

    file_format = '.tif'

    ofolder = '/home/jasp/autocls/imgsmonthrep'

    # List folders
    folders = lst_fld(fld)

    # Get reference image for each folder
    fld_ref = {}
    for f in folders:
        bf = lst_ff(f, file_format=file_format, rfilename=True)

        for b in bf:
            if 'b02' in b:
                fld_ref[f] = os.path.join(f, b)
                break
    
    # Get representative image
    for f in fld_ref:
        month_representative(
            f, fld_ref[f], ofolder,
            os.path.basename(f),
            fformat=file_format
        )

