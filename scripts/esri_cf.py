"""
Run ESRI Closest facilities
"""

if __name__ == '__main__':
    import os
    from glass.pys.oss import fprop
    from glass.g.mob.esri import closest_facility

    """
    Parameters
    """
    facilities = [
        '/home/jasp/mrgis/gigs/centrosdia.shp',
        '/home/jasp/mrgis/gigs/creches.shp',
        '/home/jasp/mrgis/gigs/Equipamentos_Desportivos.shp'
    ]
    incidents  = '/home/jasp/mrgis/gigs/bgri_pnt.shp'
    incidents_id = 'BGRI11'
    impedance = 'WalkTime'
    output = '/home/jasp/mrgis/gigs'

    """
    Run Script
    """

    for f in facilities:
        closest_facility(
            incidents, incidents_id, f,
            os.path.join(output, 'cf_{}.shp'.format(fprop(f, 'fn'))),
            impedance=impedance
        )

