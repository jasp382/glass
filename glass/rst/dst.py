"""
Raster Distance and cost
"""

def grow_distance(inrst, outrst, api="pygrass"):
    """
    Generates a raster map containing distance to nearest raster features
    """
    
    if api == 'pygrass':
        from grass.pygrass.modules import Module
    
        m = Module(
            'r.grow.distance', input=inrst, distance=outrst,
            metric='euclidean',
            overwrite=True, quiet=True, run_=False
        )
    
        m()
    
    elif api == "grass":
        from glass.pys  import execmd
        
        rcmd = execmd((
            f"r.grow.distance input={inrst} "
            f"distance={outrst} metric=euclidean "
            "--overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outrst


def rcost(cst, origin, out):
    """
    Return a acumulated cost surface
    """
    
    from grass.pygrass.modules import Module
    
    acum_cst = Module(
        'r.cost', input=cst, output=out, start_points=origin,
        overwrite=True, run_=False, quiet=True
    )
    
    acum_cst()
    
    return out

