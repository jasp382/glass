"""
Terrain GRASS GIS tools
"""


from glass.pys import execmd


def slope(demRst, slopeRst, data=None, api="pygrass"):
    """
    Get Slope Raster
    
    Data options:
    * percent;
    * degrees;
    """

    dataf = data if data == 'percent' or data == 'degrees' else 'degrees'

    if api == "pygrass":
        from grass.pygrass.modules import Module
    
        sl = Module(
            "r.slope.aspect", elevation=demRst, slope=slopeRst,
            format=dataf,
            overwrite=True, precision="FCELL", run_=False, quiet=True
        )
    
        sl()
    
    elif api == "grass":
        rcmd = execmd((
            f"r.slope.aspect elevation={demRst} "
            f"slope={slopeRst} format={dataf} "
            f"precision=FCELL --overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return slopeRst


def aspect(dem, rst_aspect, from_north=None, api="pygrass"):
    """
    Generate Aspect Raster
    """

    aspect_tmp = rst_aspect if not from_north else rst_aspect + '_normal'
    

    if api == 'pygrass':
        from grass.pygrass.modules import Module

        m = Module(
            "r.slope.aspect", elevation=dem, aspect=aspect_tmp,
            overwrite=True, precision="FCELL", run_=False, quiet=True
        )

        m()
    
    elif api == 'grass':
        rcmd = execmd((
            f"r.slope.aspect elevation={dem} aspect={aspect_tmp} "
            f"precision=FCELL --overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    if from_north:
        from glass.rst.alg import grsrstcalc

        expression = None if not from_north else (
            f"if({aspect_tmp} == 0, -1, if({aspect_tmp}"
            f" < 90, 90 - {aspect_tmp}, 450 - {aspect_tmp}))"
        )

        rrcmd = grsrstcalc(expression, rst_aspect, ascmd=True)
    
    return rst_aspect


def curvature(dem, profile, tangential, ascmd=None):
    """
    Returns profile and tangential curvature rasters
    """

    if ascmd:
        rmcd = execmd((
            f"r.slope.aspect elevation={dem} "
            f"pcurvature={profile} tcurvature="
            f"{tangential} --overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'r.slope.aspect', elevation=dem,
            pcurvature=profile, tcurvature=tangential,
            overwrite=True, run_=False, quiet=True
        )

        m()

    return profile, tangential



def paramscale(dem, size, out, ascmd=None):
    """
    Run r.param.scale
    """

    if ascmd:
        res = execmd((
            f"r.param.scale input={dem} output={out} "
            f"size={str(size)} method=feature "
            "--overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'r.param.scale', input=dem, output=out,
            size=size, method='feature',
            overwrite=True, run_=False, quiet=True
        )

        m()
    

    return out



def geomorphon(dem, out, search, skip, flat, ascmd=None):
    """
    Run r.geomorphon
    """

    if ascmd:
        res = execmd((
            f"r.geomorphon elevation={dem} forms={out} "
            f"search={search} skip={skip} flat={flat} "
            "--overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module

        m = Module(
            'r.geomorphon', elevation=dem, forms=out,
            search=search, skip=skip, flat=flat,
            overwrite=True, run_=False, quiet=True
        )

        m()
    
    return out

