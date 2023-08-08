"""
GRASS Tools
"""


def copy_insame_vector(inShp, colToBePopulated, srcColumn, destinyLayer,
                       geomType="point,line,boundary,centroid",
                       asCMD=None):
    """
    Copy Field values from one layer to another in the same GRASS Vector
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        vtodb = Module(
            "v.to.db", map=inShp, layer=destinyLayer, type=geomType,
            option="query", columns=colToBePopulated,
            query_column=srcColumn, run_=False, quiet=True,
            overwrite=True
        )
    
        vtodb()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            f"v.to.db map={inShp} layer={destinyLayer} "
            f"type={geomType} option=query columns={colToBePopulated} "
            f"query_column={srcColumn} --quiet --overwrite"
        ))

