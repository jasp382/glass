"""
Run Viewshed
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

    demrst = '/home/osmtolulc/mrgis/vistofire/cmb_dem10.tif'
    pntobs = '/home/osmtolulc/mrgis/vistofire/pnt_incendio.shp'
    obs_id = 'pnt_fid'

    """
    Run Script
    """

    from glass.geo.gt.nop.surf import thrd_viewshed_v2

    thrd_viewshed_v2('viewtofire', demrst, pntobs, obs_id)

