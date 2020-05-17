"""
Raster Distance and cost
"""

def grow_distance(inRst, outRst, api="pygrass"):
    """
    Generates a raster map containing distance to nearest raster features
    """
    
    if api == 'pygrass':
        from grass.pygrass.modules import Module
    
        m = Module(
            'r.grow.distance', input=inRst, distance=outRst, metric='euclidean',
            overwrite=True, quiet=True, run_=False
        )
    
        m()
    
    elif api == "grass":
        from glass.pyt import execmd
        
        rcmd = execmd((
            "r.grow.distance input={} distance={} metric=euclidean "
            "--overwrite --quiet"
        ).format(inRst, outRst))
    
    else:
        raise ValueError("API {} is not available".format(api))
    
    return outRst


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

