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



def feat_vertex_to_pnt(inShp, outPnt, nodes=True):
    """
    Feature Class to a Point Feature Class
    
    v.to.points - Creates points along input lines in new vector map with
    2 layers.
    
    v.to.points creates points along input 2D or 3D lines, boundaries and
    faces. Point features including centroids and kernels are copied from
    input vector map to the output. For details see notes about type parameter.
    
    The output is a vector map with 2 layers. Layer 1 holds the category of
    the input features; all points created along the same line have the same
    category, equal to the category of that line. In layer 2 each point has
    its unique category; other attributes stored in layer 2 are lcat - the
    category of the input line and along - the distance from line's start.
    
    By default only features with category are processed, see layer parameter
    for details.
    """
    
    from grass.pygrass.modules import Module
    
    toPnt = Module(
        "v.to.points", input=inShp,
        output=outPnt,
        use="node" if nodes else "vertex",
        overwrite=True, run_=False,
        quiet=True
    )
    
    toPnt()
    
    return outPnt


def line_to_polyline(inShp, outShp, asCmd=None):
    """
    v.build.polylines - Builds polylines from lines or boundaries.
    
    v.build.polylines builds polylines from the lines or boundaries in a vector map.
    
    A line is defined by one start node, one end node and any number of vertices
    between the start and end nodes. The shortest possible line consists of only two
    vertices where the coordinates of the start and end nodes are identical to
    those of the two vertices.
    
    v.build.polylines picks a line and from its start node, walks back as long
    as exactly one other line of the same type is connected to this node. Line
    directions are reversed as required, i.e. it does not matter if the next line
    is connected to the current node by its start or end node. Once the start
    line of a polyline is identified, it walks forward and adds all vertices (
    in reverse order if needed) of connected lines to the start line, i.e. the
    start line and connecting lines are reversed as needed. That is, if a line is
    reversed depends on what node is initially picked for building polylines.
    If the direction of lines is important (it's not for boundaries to build
    areas), you have to manually change line directions with either v.edit or
    the wxGUI vector digitizer.
    
    Polylines provide the most appropriate representation of curved lines when
    it is important that nodes serve to define topology rather than geometry.
    Curved lines are usually digitized as polylines, but these are sometimes
    broken into their constituent straight line segments during conversion from
    one data format to another. v.build.polylines can be used to rebuild such
    broken polylines. 
    """
    
    if not asCmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.build.polylines", input=inShp, output=outShp,
            cats='same', overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            f"v.build.polylines input={inShp} output={outShp} cats='same' "
            "--overwrite --quiet"
        ))
    
    return outShp


def geomtype_to_geomtype(inShp, outShp, fm_type, to_type, cmd=None):
    """
    v.type - Changes type of vector features.
    
    v.type changes the type of geometry primitives.
    """
    
    if not cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.type", input=inShp, output=outShp, from_type=fm_type,
            to_type=to_type, overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            f"v.type input={inShp} output={outShp} "
            f"from_type={fm_type} to_type={to_type} "
            "--overwrite --quiet"
        ))
    
    return outShp


def boundary_to_areas(inShp, outShp, useCMD=None):
    """
    v.centroids - Adds missing centroids to closed boundaries. 
    
    GRASS defines vector areas as composite entities consisting of a set of
    closed boundaries and a centroid. The attribute information associated with
    that area is linked to the centroid. The v.centroids module adds centroids
    to closed boundaries in the input file and assigns a category number to them.
    The starting value as well as the increment size may be set using optional
    parameters.
    
    Multiple attributes may be linked to a single vector entity through numbered
    fields referred to as layers. Refer to v.category for more details, as
    v.centroids is simply a frontend to that module.
    
    The boundary itself is often stored without any category reference as it can
    mark the border between two adjacent areas. Thus it would be ambiguous as to
    which feature the attribute would belong. In some cases it may, for example,
    represent a road between two parcels of land. In this case it is entirely
    appropriate for the boundary to contain category information. 
    """
    
    if not useCMD:
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.centroids", input=inShp, output=outShp,
            overwrite=True, quiet=True, run_=False
        )
        
        m()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            f"v.centroids input={inShp} output={outShp} "
            "--overwrite --quiet"
        ))
    
    return outShp

