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
        from glass.pys import execmd
        
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


def dist_from_centralcell(orst, dmax, out):
    """
    Computes a new raster with the distances from each
    cell and the central cell

    * orst - path to a raster... the origin of this raster
    will be the origin of the out rst

    * dmax - integer | distance between the raster center
    and the top/left

    * outrst - path to the output raster

    The dimension of the new raster will be based on the origin
    of the orst and the value of dmax
    """

    import math
    import numpy as np

    from glass.prop.prj import rst_epsg
    from glass.prop.rst import rst_geoprop
    from glass.wt.rst   import obj_to_rst

    # Get EPSG
    epsg = rst_epsg(orst)

    # Get Geo properties
    left, cell_x, top, cell_y = rst_geoprop(orst)

    # Get lines and columns numbers of the new raster
    ncols = (int(dmax / abs(cell_x))) * 2
    nrows = (int(dmax / abs(cell_y))) * 2

    # Get coordinates of the center cell
    irow = math.trunc(round(nrows/2, 0)) - 1
    ycenter = top + (irow + 0.5) * cell_y

    icol = math.trunc(round(ncols/2, 0)) - 1
    xcenter = left + (icol + 0.5) * cell_x

    # Generate arrays with indexes values
    # Columns Indexes
    idxcols = np.ones((nrows, ncols), np.int64)
    idxcols = np.multiply(idxcols, np.arange(0, idxcols.shape[0]))

    # Rows Indexes
    idxrows = np.transpose(idxcols)

    # Get coordinates of each cell
    coordx = np.zeros((nrows, ncols), np.float32)
    coordx = left + (idxcols + 0.5) * cell_x

    coordy = np.zeros((nrows, ncols), np.float32)
    coordy = top + (idxrows + 0.5) * cell_y

    # Get distance
    distv = np.sqrt(np.power(coordx - xcenter, 2) + \
        np.power(coordy - ycenter, 2))

    # Export new raster
    gtrans = (left, cell_x, 0,top, 0, cell_y)
    obj_to_rst(distv, out, gtrans, epsg)

    return out


def dist_from_pnt(topleft, shape, cellsize, pnt):
    """
    Computes a new raster with the distances from each
    cell and a given point
    """

    import numpy as np

    left, top = topleft
    cell_x, cell_y = cellsize
    nrows, ncols = shape

    # Reference point
    pnt_x, pnt_y = pnt

    # Generate arrays with indexes values
    # Columns Indexes
    idxcols = np.ones((nrows, ncols), np.int64)
    idxcols = np.multiply(idxcols, np.arange(0, idxcols.shape[0]))

    # Rows Indexes
    idxrows = np.transpose(idxcols)

    # Get coordinates of each cell
    coordx = np.zeros((nrows, ncols), np.float32)
    coordx = left + (idxcols + 0.5) * cell_x

    coordy = np.zeros((nrows, ncols), np.float32)
    coordy = top + (idxrows + 0.5) * cell_y

    # Get distance
    distv = np.sqrt(np.power(coordx - pnt_x, 2) + \
        np.power(coordy - pnt_y, 2))

    return distv


def dist_fmpnt_to_rst(topleft, shape, cellsize, pnt, outrst, oepsg):
    """
    Distance between each cell and point to raster
    """

    from glass.wt.rst import obj_to_rst

    left, top = topleft
    cell_x, cell_y = cellsize

    # Get distance matrix
    dist = dist_from_pnt(topleft, shape, cellsize, pnt)

    # Export to raster
    gtrans = (left, cell_x, 0,top, 0, cell_y)
    obj_to_rst(dist, outrst, gtrans, oepsg)

    return outrst

