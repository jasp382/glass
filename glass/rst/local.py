"""
Local Tools
"""

def combine(inRst, outRst, api="pygrass"):
    """
    Combine Rasters
    """
    
    if api == 'pygrass':
        from grass.pygrass.modules import Module
    
        c = Module(
            "r.cross", input=inRst, output=outRst, flags='z',
            overwrite=True, run_=False, quiet=True
        )
    
        c()
    
    elif api == "grass":
        from glass.pys import execmd
        
        rcmd = execmd((
            f"r.cross input={','.join(inRst)} output={outRst} "
            "-z --overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"API {api} is not available")
    
    return outRst

