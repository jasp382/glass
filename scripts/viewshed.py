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

    demrst = '/home/jasp/mrgis/vistofire/cmb_dem10.tif'
    pntobs = '/home/jasp/mrgis/vistofire/pnt_incendio_p3.shp'
    obs_id = 'pnt_fid'

    """
    Run Script
    """

    from gasp.gt.nop.surf import thrd_viewshed_v2

    thrd_viewshed_v2('viewtofire', demrst, pntobs, obs_id)

