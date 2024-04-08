"""
Generate dummy data for Fireloc System
"""


import numpy as np
import pandas as pd


def dummy_ctb(fires, ctbmain, ctbshp, userpos_shp, bfshp, 
              startime, endtime, nmaxctb=50):
    """
    Generate Contributions from Fire positions
    """

    import scipy.linalg as la

    from glass.rd.shp     import shp_to_obj
    from glass.it.pd      import obj_to_geodf
    from glass.smp.pnt    import get_randpnt_in_circle
    from glass.wt.shp     import df_to_shp
    from glass.gp.cnv.obj import multipart_to_single
    from glass.prop.prj   import df_epsg

    # Get fires
    fdf = shp_to_obj(fires)

    epsg = df_epsg(fdf, 'geometry')

    # Get contributions DataFrame
    ctb_df = fdf.copy()

    # Fire coordinates
    ctb_df["firex"] = ctb_df.geometry.x
    ctb_df["firey"] = ctb_df.geometry.y

    # Get Contributions ID's
    # ---------
    maxc = nmaxctb if nmaxctb > 1 else 2
    ctb_df["nctb"] = np.random.randint(1, maxc, ctb_df.shape[0])

    ctb_df = ctb_df.loc[ctb_df.index.repeat(ctb_df.nctb)]
    ctb_df.reset_index(drop=True, inplace=True)

    ctb_df['cid'] = ctb_df.index + 1
    # ---------

    # Get Contribution time
    # ---------
    # Starttime to unix
    ctb_df["stunix"] = pd.to_datetime(ctb_df[startime], format='%Y-%m-%d %H:%M:%S')
    ctb_df["stunix"] = (ctb_df.stunix - pd.Timestamp("1970-01-01")) \
        // pd.Timedelta('1s')

    # Endtime to unix
    ctb_df["endunix"] = pd.to_datetime(ctb_df[endtime], format='%Y-%m-%d %H:%M:%S')
    ctb_df["endunix"] = (ctb_df.endunix - pd.Timestamp("1970-01-01")) \
        // pd.Timedelta('1s')

    # Generate random timestamp
    ctb_df["datehour"] = np.random.randint(ctb_df.stunix, ctb_df.endunix)

    # To the correct format
    ctb_df["datehour"] = pd.to_datetime(ctb_df.datehour, unit='s')
    ctb_df["datehour"] = ctb_df.datehour.dt.strftime('%Y-%m-%d %H:%M:%S')

    tdcols = ["unix_start", "stunix", "endunix", startime, endtime]
    ctb_df.drop(tdcols, axis=1, inplace=True)
    # ---------

    # Get User Real position
    # ---------
    ctb_df = get_randpnt_in_circle(ctb_df, 10000, 'geometry', epsg)
    # ---------

    # Get Contribution positions
    # ---------
    ctb_df["npos"] = np.random.randint(50, 100, ctb_df.shape[0])
    ctb_df = ctb_df.loc[ctb_df.index.repeat(ctb_df.npos)]
    ctb_df.reset_index(drop=True, inplace=True)

    ctb_df["usergeom"]= ctb_df.geometry.to_wkt()

    ctb_df["realx"] = ctb_df.geometry.x
    ctb_df["realy"] = ctb_df.geometry.y

    ctb_df["cposdev"] = np.random.randint(1, 50, ctb_df.shape[0])
    ctb_df["cposdev"] = ctb_df.cposdev.astype(int)
    ctb_df = get_randpnt_in_circle(
        ctb_df, 'cposdev', 'geometry', epsg,
        radius_is_col=True
    )

    ctb_df = ctb_df.dissolve(by='cid')
    ctb_df.reset_index(drop=False, inplace=True)

    # Get Geometries centroid
    ctb_df["geomc"] = ctb_df.geometry.centroid

    # Geoms to string
    ctb_df["geom"]  = ctb_df.geometry.to_wkt()
    ctb_df["geomc"] = ctb_df.geomc.to_wkt()
    # ---------

    # Get Real direction to fire
    # ---------
    ctb_df['dif_x'] = ctb_df.firex - ctb_df.realx
    ctb_df['dif_y'] = ctb_df.firey - ctb_df.realy
    ctb_df['norms'] = pd.Series(data=np.linalg.norm(
        ctb_df[['dif_x', 'dif_y']], axis=1
    ))

    ctb_df["dif_x"] = ctb_df.dif_x / ctb_df.norms
    ctb_df["dif_y"] = ctb_df.dif_y / ctb_df.norms

    zonenorm = la.norm([0, 1])
    v1n = [0 / zonenorm, 1 / zonenorm]

    ctb_df["deltax"] = ctb_df.dif_x - v1n[0]
    ctb_df['dot'] = ctb_df.apply(lambda x: np.dot(v1n, [x.dif_x, x.dif_y]), axis=1)
    ctb_df["direction"] = np.arccos(ctb_df["dot"]) * 180 / np.pi

    ctb_df["direction"] = np.where(
        ctb_df.deltax >= 0, ctb_df.direction,
        -ctb_df.direction + 360
    )

    ctb_df["direction"] = ctb_df.direction.round(0).astype(int)

    ctb_df.drop(["dif_x", "dif_y", "norms", "deltax", "dot"], axis=1, inplace=True)
    # ---------

    # Get Back front direction
    # ---------
    ctb_df["desvdir"] = np.random.randint(-20, 20, ctb_df.shape[0])

    ctb_df["directbf"] = ctb_df.direction + ctb_df.desvdir
    # ---------

    # Get Back front positions
    # ---------
    ctb_df["nbf"] = np.random.randint(10, 30, ctb_df.shape[0])
    ctb_df = ctb_df.loc[ctb_df.index.repeat(ctb_df.nbf)]
    ctb_df.reset_index(drop=True, inplace=True)

    sign = np.random.randint(0, 1, ctb_df.shape[0])

    ctb_df["bfx"] = np.where(
        sign == 1, ctb_df.realx + 5 * np.cos(ctb_df.direction),
        ctb_df.realx - 5 * np.cos(ctb_df.direction)
    )

    ctb_df["bfy"] = np.where(
        sign == 1, ctb_df.realy + 5 * np.cos(ctb_df.direction),
        ctb_df.realy - 5 * np.cos(ctb_df.direction)
    )

    ctb_df.drop(["geometry"], axis=1, inplace=True)

    ctb_df["bfposdev"] = np.random.randint(1, 50, ctb_df.shape[0])
    ctb_df["bfposdev"] = ctb_df.bfposdev.astype(int)
    ctb_df = get_randpnt_in_circle(
        ctb_df, 'bfposdev', ("bfx", "bfy"), epsg=epsg,
        radius_is_col=True
    )

    ctb_df = ctb_df.dissolve(by='cid')
    ctb_df.reset_index(drop=False, inplace=True)

    # Get geombf centroid
    ctb_df["geombfc"] = ctb_df.geometry.centroid

    # Geom to string
    ctb_df["geombf"]  = ctb_df.geometry.to_wkt()
    ctb_df["geombfc"] = ctb_df.geombfc.to_wkt()

    ctb_df.drop("geometry", axis=1, inplace=True)
    # ---------

    # Export Data to ESRI Shapefile
    # ---------
    dcols = [
        "firex", "firey", 'pid', 'nctb',
        'npos', 'realx', 'realy', 'cposdev',
        "geomc", "desvdir", "bfx", "bfy",
        "bfposdev", "geom", "geombf", "usergeom",
        "nbf", "geombfc"
    ]

    expd = {
        ctbshp       : "geom",
        userpos_shp  : "usergeom",
        bfshp        : "geombf"
    }

    for k in expd:
        ndf = ctb_df.copy()

        ndf["geometry"] = ndf[expd[k]].copy()
        ndf = obj_to_geodf(ndf, 'geometry', epsg)

        if expd[k] == 'geom' or expd[k] == 'geombf':
            ndf = multipart_to_single(ndf, 'Point', epsg)

        ndf.drop(dcols, axis=1, inplace=True)

        df_to_shp(ndf, k)
    # ---------

    # Get Contributions Main table
    mdf = ctb_df.copy()

    mdf["geometry"] = mdf.geomc.copy()

    mdf.rename(columns={'cid' : 'ctbid'}, inplace=True)

    mdf.drop(["geom", "geombf", "usergeom"], axis=1, inplace=True)

    mdf["geometry"] = mdf.geometry.astype(str)

    mdf.drop(dcols, axis=1, inplace=True)
    mdf = obj_to_geodf(mdf, "geometry", epsg)
    df_to_shp(mdf, ctbmain)

    return ctbmain, ctbshp, userpos_shp, bfshp

