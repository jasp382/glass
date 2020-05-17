"""
Tools to help validate high resolution layers
"""

import os
import pandas as pd


def osm_vs_imd(osmshp, imdrst, outshp, outrst=None):
    """
    This program compare selected OSM data in Portugal with high-resolution-layers (imperviousness density maps) from Copernicus.
    The objective is:
    - Create a fishnet whit 10m, same cellsize of idm;
    - Intersect OSM data with fishnet;
    - Insert the value of the OSM area in the fishnet cell
    - Export shapefile and raster all information of this iterate 
    """

    from glass.pys.oss  import mkdir, fprop
    from glass.wenv.grs import run_grass
    from glass.smp.fish import nfishnet_fm_rst
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import df_to_shp
    from glass.dtt.mge  import shps_to_shp

    obname = fprop(outshp, 'fn')

    ws  = mkdir(os.path.join(
        os.path.dirname(outshp), f"tmp{obname}"
    ), overwrite=True)

    # Create fishnet based on imdrst
    fishfolder = mkdir(os.path.join(ws, 'fishnet'))
    fishnets   = nfishnet_fm_rst(imdrst, 500, 500, fishfolder)

    # Start GRASS GIS Session
    loc = f"loc_{obname}"

    gb = run_grass(ws, location=loc, srs=imdrst)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    # GRASS GIS Modules
    from glass.it.shp        import shp_to_grs, grs_to_shp
    from glass.it.rst        import rst_to_grs, grs_to_rst
    from glass.gp.gen        import dissolve
    from glass.tbl.col       import add_fields, cols_calc
    from glass.gp.ovl.grs    import grsintersection
    from glass.smp.pnt       import sample_to_points
    from glass.dtt.rst.torst import grsshp_to_grsrst

    # Import data
    osmgrs = shp_to_grs(osmshp, fprop(osmshp, 'fn'), filterByReg=True)
    imdgrs = rst_to_grs(imdrst, fprop(imdrst, 'fn'))

    # Dissolve
    add_fields(osmgrs, {'gencol': 'integer'}, api="grass")
    cols_calc(osmgrs, "gencol", 1, "gencol IS NULL", ascmd=None)

    osmdiss = dissolve(osmgrs, 'osmdissolve', "gencol", api='grass')

    # For each fishnet
    fishres = []
    for fshp in fishnets:
        fnetgrs = shp_to_grs(fshp, fprop(fshp, 'fn'))

        # Intersect fishnet with osm polygons
        iosmfish = grsintersection(fnetgrs, osmdiss, f'i_{fnetgrs}')

        # Export intersection result to file
        ishp = grs_to_shp(iosmfish, os.path.join(
            ws, f"{iosmfish}.shp"
        ), 'area')

        # Export fishnet centroids
        fishpnt = grs_to_shp(fnetgrs, os.path.join(
            ws, f'pnt_{fnetgrs}.shp'
        ), 'centroid')

        # Import centroids
        pntgrs = shp_to_grs(fishpnt, fprop(fishpnt, 'fn'))

        # Extract IMD values to points
        add_fields(pntgrs, {'imdval' : "double precision"}, api="grass")
        sample_to_points(pntgrs, 'imdval', imdgrs)

        # Export points with raster values
        pntval = grs_to_shp(pntgrs, os.path.join(
            ws, f'{pntgrs}_val.shp'
        ), 'point')

        # Read data as Dataframes
        idf    = shp_to_obj(ishp)
        fishdf = shp_to_obj(fshp)
        pdf    = shp_to_obj(pntval)

        idf = idf[~idf.a_cat.isna()]
        idf['a_cat'] = idf.a_cat.astype(int)

        # Get field with area
        idf["garea"] = idf.geometry.area

        # Get area with OSM data in each cell
        areabycell = pd.DataFrame({
            'iarea' : idf.groupby(['a_cat'])['garea'].agg('sum')
        }).reset_index()

        # Join with original fishnet
        fishdf['cellid'] = fishdf.index + 1

        fishdf = fishdf.merge(
            areabycell, how='left', left_on='cellid', right_on='a_cat'
        )

        fishdf['iarea'] = fishdf.iarea.fillna(value=0)

        fishdf["urbanp"] = fishdf.iarea * 100 / fishdf.geometry.area

        # Get IMD Values
        dpcols = [c for c in pdf.columns.values if c != 'imdval']
        pdf.drop(dpcols, axis=1, inplace=True)
        pdf['pid'] = pdf.index + 1

        fishdf = fishdf.merge(pdf, how='left', left_on="cellid", right_on="pid")
        fishdf.drop(["a_cat", "pid"], axis=1, inplace=True)

        # Save result
        fshwd = df_to_shp(fishdf, os.path.join(ws, f'vsimd_{fnetgrs}.shp'))

        fishres.append(fshwd)
    
    # Merge Shapefiles
    shps_to_shp(fshwd, outshp, api="pandas")

    # Shapefile to Raster
    if outrst:
        outgrs = shp_to_grs(outshp, fprop(outshp, 'fn'))

        rstgrs = grsshp_to_grsrst(outgrs, 'urbanp', fprop(outrst, 'fn'))

        grs_to_rst(rstgrs, outrst, as_cmd=True, rtype=float)

    return outshp





def osmvsimd_multiproc(imdfolder, osmfolder, ofolder):
    """
    Run osm_vs_imd on a multi thread approach
    """


    import datetime as dt

    from glass.pys.oss  import lst_ff

    now    = dt.datetime.utcnow().replace(microsecond=0)
    nowstr = now.strftime('%Y%m%d%H%M%S')

    logf = os.path.join(ofolder, f"log_{nowstr}.json")

    imddf = pd.DataFrame([{
        'imdid' : int(f.split('.')[0].split('_')[-1]),
        'imd'   : f
    } for f in lst_ff(
        imdfolder, rfilename=True, file_format='.shp'
    )])

    osmdf = pd.DataFrame([{
        'osmid'  : int(f.split('.')[0].split('_')[-1]),
        'osmshp' : f
    } for f in lst_ff(
        osmfolder, rfilename=True, file_format='.shp'
    )])

    imdf = imddf.merge(osmdf, how="outer", left_on="imdid", right_on="osmid")

    imdf = imdf[~imdf.imd.isna()]
    imdf = imdf[~imdf.osmshp.isna()]

    return ofolder

