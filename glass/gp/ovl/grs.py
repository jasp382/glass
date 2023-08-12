"""
GRASS GIS Overlay tools
"""

from glass.pys import execmd


def grsunion(lyra, lyrb, oshp, cmd=None):
    """
    GRASS Union
    """

    if cmd:
        outcmd = execmd((
            f"v.overlay ainput={lyra} atype=area "
            f"binput={lyrb} btype=area "
            f"operator=or output={oshp} --overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module
        
        un = Module(
            "v.overlay", ainput=lyra, atype="area",
            binput=lyrb, btype="area", operator="or",
            output=oshp, overwrite=True, run_=False, quiet=True
        )
        
        un()

    return oshp


def grsintersection(inshp, intshp, outshp, cmd=None):
    """
    GRASS GIS intersection
    """

    if cmd:
        rcmd = execmd((
            f"v.overlay ainput={inshp} atype=area, "
            f"binput={intshp} btype=area "
            f"operator=and output={outshp} --overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module
        
        tool = Module(
            "v.overlay", ainput=inshp, atype="area",
            binput=intshp, btype="area", operator="and",
            output=outshp,  overwrite=True, run_=False, quiet=True
        )
        
        tool()
    
    return outshp


def grs_select(ashp, bshp, oshp, operator, cmd=True):
    """
    v.select allows the user to select features from a vector map by features from another one.

    Supported operators (without GEOS; using GRASS' own algorithm):

        overlap - features partially or completely overlap (GEOS equivalent: intersects) 

    Supported operators (internally using GEOS - Geometry Engine, Open Source):

        equals - features are spatially equals
        disjoint - features do not spatially intersect
        intersects - features spatially intersect (equivalent to native 'overlap')
        touches - features spatially touches
        crosses - features spatially crosses
        within - feature A is completely inside feature B
        contains - feature B is completely inside feature A
        overlaps - features spatially overlap
        relate - feature A is spatially related to feature B
    """

    if cmd:
        rcmd = execmd((
            f"v.select ainput={ashp} binput={bshp} "
            f"output={oshp} operator={operator} "
            "--overwrite --quiet"
        ))

    else:
        from grass.pygrass.modules import Module

        tool = Module(
            "v.select", ainput=ashp, binput=bshp,
            output=oshp, operator=operator,
            overwrite=True, run_=False, quiet=True
        )

        tool()
    
    return output

