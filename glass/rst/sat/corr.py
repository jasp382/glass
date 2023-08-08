"""
Satellite Data Correction
"""


def landsat_toar(iprefix, oprefix, metatxt, ascmd=True):
    """
    Apply toar procedure to landsat image bands

    sensor=string
        Spacecraft sensor
        Required only if 'metfile' not given (recommended for sanity)
        Options: mss1, mss2, mss3, mss4, mss5, tm4, tm5, tm7, oli8
        mss1: Landsat-1 MSS
        mss2: Landsat-2 MSS
        mss3: Landsat-3 MSS
        mss4: Landsat-4 MSS
        mss5: Landsat-5 MSS
        tm4: Landsat-4 TM
        tm5: Landsat-5 TM
        tm7: Landsat-7 ETM+
        oli8: Landsat_8 OLI/TIRS
    
    method=string
        Atmospheric correction method
        Options: uncorrected, dos1, dos2, dos2b, dos3, dos4
        Default: uncorrected
    """

    if not ascmd:
        from grass.pygrass.modules import Module

        m = Module(
            'i.landsat.toar', input=iprefix,
            output=oprefix,
            metfile=metatxt, method='dos4',
            overwrite=True, run_=False, quiet=True
        )

        m()
    
    else:
        from glass.pys import execmd

        cmd = execmd((
            f"i.landsat.toar input={iprefix} "
            f"output={oprefix} metfile={metatxt} "
            "method=dos4 --overwrite --quiet"
        ))



def landsat_topocorr(dem, zenith, azimuth, out, ascmd=True):
    """
    Landsat Topographic Correction
    """

    if not ascmd:
        from grass.pygrass.modules import Module

        m = Module(
            'i.topo.corr', basemap=dem, output=out,
            zenith=zenith, azimuth=azimuth,
            flags='i',
            overwrite=True, run_=False, quiet=True
        )

        m()
    
    else:
        from glass.pys import execmd

        cmd = execmd((
            f"i.topo.corr output={out} "
            f"basemap={dem} zenith={str(zenith)} "
            f"azimuth={str(azimuth)} "
            "-i --overwrite --quiet"
        ))

    return out

