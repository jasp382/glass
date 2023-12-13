"""
Direction and Angles
"""

def angrst_from_pnt(topleft, shape, cellsize, pnt, outrst, oepsg, resint=None):
    """
    Produce raster with angles from 0 to 360 in relation
    to a given point
    """

    import numpy as np
    import scipy.linalg as la

    from glass.wt.rst import obj_to_rst

    # Get Geo properties
    left, top = topleft
    nrows, ncols = shape
    cellx, celly = cellsize

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
    coordx = left + (idxcols + 0.5) * cellx

    coordy = np.zeros((nrows, ncols), np.float32)
    coordy = top + (idxrows + 0.5) * celly

    # Get distance array
    difx = coordx - pnt_x
    dify = coordy - pnt_y

    v2 = np.zeros((nrows, ncols, 2), np.float32)
    v2[:, :, 0] = difx
    v2[:, :, 1] = dify

    # Get angles values
    v1 = np.array([0.0, 1.0])

    v2norm = np.linalg.norm(v2, axis=2)

    v2[:, :, 0] = np.where(
        v2norm == 0, 0,
        v2[:, :, 0] / v2norm
    )

    v2[:, :, 1] = np.where(
        v2norm == 0, 0,
        v2[:, :, 1] / v2norm
    )

    v1 = v1 / la.norm(v1)

    sinang = np.cross(v1, v2[:, :])

    dot = np.tensordot(v1, v2, axes=(0, 2))

    ang = np.arccos(dot) * 180 / np.pi

    ang = np.where(
        sinang >= 0, -ang + 360, ang
    )

    if resint:
        ang = np.round_(ang, decimals=0)

        ang = ang.astype(np.int16)
    
    # Export new raster
    gtrans = (left, cellx, 0, top, 0, celly)

    obj_to_rst(ang, outrst, gtrans, oepsg)

    return outrst


def bearing_from_pnt(topleft, shape, cellsize, pnt, resint=None):
    """
    Bearing from each cell and point
    """

    import numpy as np

    # Get Geo properties
    left, top = topleft
    nrows, ncols = shape
    cellx, celly = cellsize

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
    coordx = left + (idxcols + 0.5) * cellx

    coordy = np.zeros((nrows, ncols), np.float32)
    coordy = top + (idxrows + 0.5) * celly

    # Get bearing from each cell and reference point

    # Get distance array
    difx = coordx - pnt_x
    dify = coordy - pnt_y

    # Bearing calculation
    bearing = np.degrees(np.arctan2(difx, dify))

    bearing = np.where(
        bearing < 0, bearing + 360,
        bearing
    )

    if resint:
        bearing = np.round_(bearing, decimals=0)

    return bearing


def bearing_fmpnt_to_rst(topleft, shape, cellsize, pnt, outrst, oepsg, resint=None):
    """
    Bearing from each cell and point to raster
    """

    from glass.wt.rst import obj_to_rst

    # Get Geo properties
    left, top = topleft
    cellx, celly = cellsize

    # Get bearing
    bearing = bearing_from_pnt(topleft, shape, cellsize, pnt, resint=resint)

    # Export new raster
    gtrans = (left, cellx, 0, top, 0, celly)

    obj_to_rst(bearing, outrst, gtrans, oepsg)

    return outrst


def grs_bearing_from_pnt(pnt, orst, asint=None):
    """
    Generate bearing raster - bearing from each cell to a specific
    point
    """

    from glass.rst.alg import grsrstcalc

    pnt_x, pnt_y = pnt

    # Bearing
    bearing = grsrstcalc(
        f"atan(y() - {str(pnt_y)}, x() - {str(pnt_x)})",
        "bearing", ascmd=True
    )

    exp = (
        f"{'int(round(' if asint else ''}"
        f"if({bearing} < 0, {bearing} + 360, {bearing})"
        f"{'))' if asint else ''}"
    )


    bearing = grsrstcalc(exp, orst, ascmd=True)

    return orst


def angrst_centercell(orst, dmax, outrst, resint=None):
    """
    Produce raster with angles from 0 to 360 in relation
    to the central cell

    * orst - path to a raster... the origin of this raster
    will be the origin of the out rst

    * dmax - integer | distance between the raster center
    and the top/left

    * outrst - path to the output raster
    """

    import math
    import numpy as np
    import scipy.linalg as la

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

    # Idx of the center cell
    irows = math.trunc(round(nrows/2, 0)) - 1
    icols = math.trunc(round(ncols/2, 0)) - 1

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

    numxy = np.zeros((nrows, ncols, 2), np.float32)
    numxy[:, :, 0] = coordx
    numxy[:, :, 1] = coordy

    # Get angles values
    v1 = np.array([0.0, 1.0])
    v2 = numxy - numxy[irows, icols]

    v2norm = np.linalg.norm(v2, axis=2)

    v2[:, :, 0] = np.where(
        v2norm == 0, 0,
        v2[:, :, 0] / v2norm
    )

    v2[:, :, 1] = np.where(
        v2norm == 0, 0,
        v2[:, :, 1] / v2norm
    )

    v1 = v1 / la.norm(v1)
    
    sinang = np.cross(v1, v2[:, :])
    
    dot = np.tensordot(v1, v2, axes=(0, 2))

    ang = np.arccos(dot) * 180 / np.pi

    ang = np.where(
        sinang >= 0, -ang + 360, ang
    )
    
    if resint:
        ang = np.round_(ang, decimals=0)

        ang = ang.astype(np.int16)

    # Export new raster
    gtrans = (left, cell_x, 0,top, 0, cell_y)

    obj_to_rst(ang, outrst, gtrans, epsg)

    return outrst

