"""
Watershed related tools
"""


def flow_accum(elevrst, flowacc, dir_rst=None, ascmd=None):
    """
    Produce flow accumulation raster

    if dir_rst is true, produce flow direction raster
    """

    if ascmd:
        from glass.pys import execmd

        rcmd = execmd((
            f"r.watershed -sa elevation={elevrst} "
            f"accumulation={flowacc} "
            f"{f'drainage={dir_rst} ' if dir_rst else ''}"
            f"--overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        gm = Module(
            "r.watershed", elevation=elevrst,
            accumulation=flowacc, drainage=dir_rst,
            flags='sa', run_=False, quiet=True
        )

        gm()
    
    return flowacc, dir_rst


def twi(elevrst, twi, ascmd=None):
    """
    Produce Topographic Wetness index using GRASS GIS
    """

    if ascmd:
        from glass.pys import execmd

        rcmd = execmd((
            f"r.watershed -sa elevation={elevrst} "
            f"tci={twi} "
            f"--overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        gm = Module(
            "r.watershed", elevation=elevrst,
            tci=twi,
            flags='sa', run_=False, quiet=True
        )

        gm()
    
    return twi

