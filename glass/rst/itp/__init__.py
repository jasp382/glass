"""
Interpolation Tools
"""

import os

from glass.wenv.grs import grass_session


def surf_rst(ishp, col, orst, ws=None, cellsize=10):
    """
    v.surf.rast implementation
    """

    from glass.pys.oss import fprop
    from glass.pys.tm  import now_as_str
    from glass.dtt.rst.torst  import shpext_to_rst

    # Get Reference Raster
    rref = shpext_to_rst(ishp, os.path.join(
        os.path.dirname(ishp),
        f'ref_{fprop(orst, "fn")}.tif'
    ), cellsize=cellsize)

    # Start GRASS GIS Session
    ws = ws if ws else os.path.dirname(orst)

    locn = now_as_str()

    gb = grass_session(ws, loc=locn, srs=rref)

    from glass.it.rst      import grs_to_rst
    from glass.it.shp      import shp_to_grs
    from glass.rst.itp.grs import surfrst

    # Import input data
    grs_shp = shp_to_grs(ishp, fprop(ishp, 'fn'))

    # Run Interpolation
    out_grsrst = surfrst(grs_shp, col, fprop(orst, 'fn'), lyrN=1, ascmd=True)

    # Export result
    grs_to_rst(out_grsrst, orst, dtype="Float32")

    return orst

