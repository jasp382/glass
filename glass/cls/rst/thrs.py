"""
Test thresholds in classification processes
"""

import os
import pandas as pd


def binclass_of_rst_using_thresholds(irst, thresholds, valpoints, refcol, out=None):
    """
    Test different thresholds for a binary classification
    """
    
    from glass.wenv.grs import grass_session
    from glass.pys.oss  import mkdir

    # Start GRASS GIS Session
    ws, loc = mkdir(os.path.dirname(irst), timerand=True), 'gloc'

    gb = grass_session(ws, loc=loc, srs=irst)

    from glass.cls.eval.obj import df_bincls_to_mtx
    from glass.it.rst       import rst_to_grs, grs_to_rst
    from glass.rst.alg      import grsrstcalc
    from glass.it.shp       import shp_to_grs, grs_to_shp
    from glass.smp.pnt      import sample_to_points
    from glass.rd.shp       import shp_to_obj
    from glass.wt           import obj_to_tbl

    # Import raster to GRASS GIS
    grst = rst_to_grs(irst)

    # Generate classified rasters and export them
    res = {}
    for th in thresholds:
        tstr = str(th)
        if '.' in tstr:
            tstr = tstr.replace('.', '').replace('-', 'm')

        nrst = grsrstcalc(f"if({grst} > {str(th)}, 1, 0)", f"{grst}_{tstr}")

        frst = grs_to_rst(
            nrst, os.path.join(ws, f'{nrst}.tif'),
            as_cmd=True, dtype='Byte', nodata=255
        )

        res[th] = nrst
    
    # Import validation points
    gval = shp_to_grs(valpoints)

    # Extract values of each raster
    for k in res:
        sample_to_points(gval, res[k], res[k])
    
    # Export to GeoPackage
    gpkg = grs_to_shp(
        gval, os.path.join(ws, f'{gval}.gpkg'),
        'point', lname=gval
    )

    # Open Table and compute confusion matrix
    gdf = shp_to_obj(gpkg, lyr=gval)

    mtxs, meas = [], []
    ftbl = []

    cols = [
        'raster', 'threshold',
        'TP', 'TN', 'FP', 'FN',
        'ACC', 'TPR', 'TNR', 'PRECISION',
        'FPR', 'F1'
    ]

    for t in thresholds:
        mtx, measures = df_bincls_to_mtx(
            gdf, refcol, res[t], 1, 0
        )

        ftbl.append([
            res[t], t,
            mtx.iloc[0, 1],
            mtx.iloc[1, 2],
            mtx.iloc[0, 2],
            mtx.iloc[1, 1],
            measures.iloc[1, 1],
            measures.iloc[3, 1],
            measures.iloc[4, 1],
            measures.iloc[5, 1],
            measures.iloc[6, 1],
            measures.iloc[9, 1],
        ])

        mtxs.append(mtx)
        meas.append(measures)
    
    # Compute final table
    fdf = pd.DataFrame(ftbl, columns=cols)

    if out:
        obj_to_tbl(fdf, out)

    return fdf if not out else out

