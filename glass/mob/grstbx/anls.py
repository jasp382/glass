"""
Run network analysis tools
"""

from glass.pys import execmd


def netpath(network, fileCats, fromToCol, toFromCol, outResult,
            arcLyr=1, nodeLyr=2):
    """
    Implementation of v.net.path
    """
    
    from grass.pygrass.modules import Module
    
    m = Module(
        "v.net.path", input=network, file=fileCats,
        output=outResult, arc_layer=arcLyr, node_layer=nodeLyr,
        arc_column=fromToCol, arc_backward_column=toFromCol,
        overwrite=True, run_=False
    )
    
    m()
    
    return outResult


def run_allpairs(rdv, fromto, tofrom, mtx, arclyr=1, nodelyr=2, ascmd=None):
    """
    Implementation of v.net.allpairs
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        m = Module(
            "v.net.allpairs", input=rdv, output=mtx,
            arc_layer=arclyr, node_layer=nodelyr, arc_column=fromto,
            arc_backward_column=tofrom, overwrite=True, run_=False
        )
    
        m()
    
    else:
        rcmd = execmd((
            f"v.net.allpairs input={rdv} output={mtx} "
            f"arc_layer={str(arclyr)} node_layer={str(nodelyr)} "
            f"arc_column={fromto} arc_backward_column={tofrom} "
            f"--overwrite --quiet"
        ))
    
    return mtx


def closest_facility(rdv, fromto, tofrom, res, arclyr=1, fmlyr=2, tolyr=3, ascmd=True):
    """
    v.net.distance - Computes shortest distance via the network
    between the given sets of features.
    
    Finds the shortest paths from each 'from' point to the nearest 'to' 
    feature and various information about this relation 
    are uploaded to the attribute table.
    """

    if not ascmd:
        from grass.pygrass.modules import Module
    
        m = Module(
            "v.net.distance", input=rdv, output=res,
            arc_layer=str(arclyr), from_layer=str(fmlyr), to_layer=str(tolyr),
            arc_column=fromto, arc_backward_column=tofrom,
            overwrite=True, run_=False
        )
    
        m()
    
    else:
        rcmd = execmd((
            f"v.net.distance input={rdv} output={res} "
            f"arc_layer={str(arclyr)} from_layer={fmlyr} "
            f"to_layer={str(tolyr)} "
            f"arc_column={fromto} arc_backward_column={tofrom} "
            "--overwrite --quiet"
        ))
    
    return res

