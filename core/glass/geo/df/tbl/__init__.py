"""
GIS Table Support
"""

def category(inShp, outShp, useOption, LyrN="1",
             geomType="point,line,boundary,centroid,area,face,kernel",
             asCMD=None):
    """
    v.category attaches, copies, deletes or reports categories of vector
    geometry objects. Further on, v.category adds a number given by the
    cat option to categories of the selected layer. These categories (IDs)
    are used to assign IDs or to group geometry objects into categories
    (several different geometry objects share the same category).
    These categories are also used to link geometry object(s) to attribute
    records (from an attribute table linked to vector map).
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        vcat = Module(
            "v.category", input=inShp, layer=LyrN, type=geomType,
            output=outShp, option=useOption, cat=1,
            overwrite=True, run_=False
        )
    
        vcat()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.category input={} layer={} type={} output={} "
            "option={} cat=1 --overwrite --quiet"
        ).format(inShp, LyrN, geomType, outShp, useOption))
    
    return outShp