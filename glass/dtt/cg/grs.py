"""
GRASS GIS Tools
"""

def v_to_lines(ivec: str, ovec:str,
               as_cmd: bool|None=None):
    """
    v.to.lines - Converts vector polygons or points to lines.
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.to.lines", input=ivec, output=ovec,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            f"v.in.ogr input={ivec} "
            f"output={ovec} "
            "--overwrite --quiet"
        ))
    
    return ovec

