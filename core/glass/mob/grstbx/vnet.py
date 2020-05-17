"""
GIS API's subpackage:

GRASS GIS Python tools for network analysis
"""


"""
Create and Mantain network
"""
def network_from_arcs(networkFC, networkOUT):
    """
    v.net is used for network preparation and maintenance. Its main use is
    to create a vector network from vector lines (arcs ) and points (nodes)
    by creating nodes from intersections in a map of vector lines
    (node operator), by connecting a vector lines map with a points map
    (connect operator), and by creating new lines between pairs of
    vector points (arcs operator).
    
    v.net offers two ways to add nodes to a network of arcs
    and one method to add arcs to a set of nodes.
    This tool implement one of them:
    
    Create nodes and arcs from a vector line/boundary file using the node
    operation. This is useful if you are mostly interested in the network
    itself and thus you can use intersections of the network as start and
    end points. Nodes will be created at all intersections of two or more
    lines. For an arc that consists of several segments connected by vertices
    (the typical case), only the starting and ending vertices are treated
    as network nodes.
    """
    
    from grass.pygrass.modules import Module
    
    m = Module(
        "v.net", input=networkFC, output=networkOUT,
        operation="nodes", arc_type='line',
        overwrite=True, run_=False
    )
    
    m()
    
    return networkOUT


def add_pnts_to_network(network, pntLyr, outNetwork, __threshold=200, asCMD=None):
    """
    Connect points to GRASS GIS Network
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        m = Module(
            "v.net", input=network, points=pntLyr, operation="connect",
            threshold=__threshold, output=outNetwork, overwrite=True, run_=False
        )
    
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.net input={} points={} operation=connect threshold={} "
            "output={} --overwrite --quiet"
        ).format(network, pntLyr, __threshold, outNetwork))
    
    return outNetwork



"""
Produce indicators
"""

def run_allpairs(network, fromToCol, toFromCol, outMatrix, arcLyr=1, nodeLyr=2,
                 asCMD=None):
    """
    Implementation of v.net.allpairs
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
    
        m = Module(
            "v.net.allpairs", input=network, output=outMatrix,
            arc_layer=arcLyr, node_layer=nodeLyr, arc_column=fromToCol,
            arc_backward_column=toFromCol, overwrite=True, run_=False
        )
    
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.net.allpairs input={} output={} arc_layer={} "
            "node_layer={} arc_column={} arc_backward_column={} "
            "--overwrite --quiet"
        ).format(
            network, outMatrix, str(arcLyr), str(nodeLyr), fromToCol,
            toFromCol
        ))
    
    return outMatrix


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

