"""
Terrain
"""


###############################################################################
###############################################################################
"""
Run this beutiful script
"""

if __name__ == '__main__':
    """
    Parameters
    """

    lmt_fld       = '/home/jasp/mrgis/mdt10_lmt'
    countours_fld = '/home/jasp/mrgis/srtm30_parts'
    dem_fld       = '/home/jasp/mrgis/dem_srtm_cubic'
    elv_fld       = 'elevation'
    masks         = '/home/jasp/mrgis/mdt10_masks'
    method        = 'BSPLINE'

    """
    Run Script
    """

    from glass.geo.terrain.grs import thrd_dem

    thrd_dem(
        countours_fld, lmt_fld, dem_fld, elv_fld,
        refFormat='.tif', countoursFormat='.shp', demFormat='.tif',
        cellsize=10, masksFolder=masks, masksFormat='.tif',
        method=method
    )

