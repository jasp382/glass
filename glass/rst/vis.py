


def visdb_to_rst(demrst, pntobs, obs_id, db, orst):
    """
    demrst = '/home/osmtolulc/mrgis/vistofire/cmb_dem10.tif'
    pntobs = '/home/osmtolulc/mrgis/vistofire/pnt_incendio.shp'
    obs_id = 'pnt_fid'
    """

    pnt_id = [1, 2]

    import numpy as np
    from osgeo import gdal

    from glass.sql.q  import q_to_obj
    from glass.it.rst import obj_to_rst

    # Get Raster Shape
    rsrc = gdal.Open(demrst, gdal.GA_ReadOnly)

    rows, cols = rsrc.RasterYSize, rsrc.RasterXSize

    # Get Array with cells with visibility == 1
    whr = " OR ".join([
        f"pntid = {str(p)}" for p in pnt_id
    ])

    q = (
        "SELECT idx FROM ("
            "SELECT generate_series("
                f"(rowi * {str(cols)}) + coli, "
                f"(rowe * {str(cols)}) + cole "
            ") AS idx "
            "FROM vistoburn "
            f"WHERE {whr}"
        ") AS foo "
        "GROUP BY idx "
        "ORDER BY idx"
    )

    visidx = q_to_obj(db, q, db_api='psql')

    allidx = np.arange(rows * cols).astype(np.uint32)
    visimg = np.zeros(rows * cols)

    np.place(visimg, np.isin(allidx, visidx.idx), 1)

    visimg = visimg.reshape((rows, cols))

    obj_to_rst(visimg,orst, rsrc, noData=0)

    return db

