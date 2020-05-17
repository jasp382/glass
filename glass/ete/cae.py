"""
Compare CAE with data sources
"""

import os
from glass.pys.oss import mkdir

def cae_vs_polygon(caeshp, polyshp, lulccls_col, refshp, oshp, source, polycae=None,
    ws=None, loc=None):
    """
    Compare OSM, IRD and Built up Data with
    Carta Áreas Edificadas from DGT
    """

    import pandas      as pd
    import numpy       as np
    from glass.pys.oss   import fprop
    from glass.dtt.rst.torst  import shp_to_rst
    from glass.wenv.grs  import run_grass
    from glass.rd.shp    import shp_to_obj
    from glass.wt.shp    import df_to_shp
    from glass.prop.feat import feat_count

    # Check number of features in each shape
    npoly = feat_count(polyshp, gisApi="ogr")

    if not npoly:
        return None
    
    ncae = feat_count(caeshp, gisApi="ogr")

    # Prepare workspace
    ws = os.path.dirname(oshp) if not ws else ws
    loc = f"loc_{fprop(oshp, 'fn')}" if not loc else loc

    # Dissolve all lulc classes polygons and intersect polygons with CAE
    # Start GRASS GIS Session

    bname = fprop(refshp, 'fn')

    refrst = shp_to_rst(refshp, None, 10, 0, os.path.join(
        ws, f'rst{bname}.tif'
    ), api='pygdal')

    gb = run_grass(ws, location=loc, srs=refrst, grassBIN="grass78")

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    # GRASS GIS Modules
    from glass.it.shp  import shp_to_grs, grs_to_shp
    from glass.tbl.grs import add_table
    from glass.gp.gen  import dissolve
    from glass.gp.ovl.grs  import grsunion

    # Import data
    pbname = fprop(polyshp, 'fn')
    polyg  = shp_to_grs(polyshp, olyr=pbname)
    caegrs = shp_to_grs(caeshp) if ncae else None

    # Dissolve
    lulcdiss = dissolve(polyg, f'{pbname}_d', lulccls_col, api="grass")

    add_table(lulcdiss, None, lyrN=1, asCMD=True, keyp=lulccls_col)

    disscat = grs_to_shp(lulcdiss, os.path.join(
        ws, f'{lulcdiss}.shp'
    ), 'area')

    if not ncae:
        polydf = shp_to_obj(disscat)

        polydf['fonte'] = source

        polydf.rename(columns={
            'cat' : "id_obj", lulccls_col : 'classuos'
        }, inplace=True)

        polydf['classuos'] = polydf.classuos.astype(str)
        polydf['existcae'] = 0
        polydf['existcae'] = polydf.existcae.astype(int)
        polydf['areaha']   = polydf.geometry.area / 10000

        df_to_shp(polydf, oshp)

        return oshp

    lulcdiss = shp_to_grs(disscat, olyr=fprop(disscat, 'fn') + 'v2')

    # Union Polygon and CAE
    polcae = grsunion(lulcdiss, caegrs, 'caeunion')

    # Export
    polycae = os.path.join(ws, loc, 'polyvscae.shp') if not polycae else \
        polycae
    poly_and_cae = grs_to_shp(polcae, polycae, 'area')

    # Classify polygons
    gdf = shp_to_obj(poly_and_cae)

    polydf = shp_to_obj(disscat)

    gdf = gdf[~gdf.a_cat.isna()]

    gdf['a_cat'] = gdf.a_cat.astype(int)
    gdf['b_cat'] = gdf.b_cat.fillna(value=0)
    gdf['b_cat'] = gdf.b_cat.astype(int)

    # Count how many times we have the same a_cat
    catcount = pd.DataFrame({
        'countcat' : gdf.groupby(['a_cat'])['a_cat'].agg('count')
    }).reset_index()

    catcount.rename(columns={'a_cat': 'acaty'}, inplace=True)

    # Join
    gdf = gdf.merge(catcount, how='inner', left_on='a_cat', right_on='acaty')

    # Get classes
    gdf['fcat'] = -1

    gdf['fcat'] = np.where(
        (gdf.countcat == 1) & (gdf.b_cat == 0),
        0, gdf.fcat
    )

    gdf['fcat'] = np.where(
        (gdf.countcat == 1) & (gdf.b_cat > 0),
        1, gdf.fcat
    )

    gdf['fcat'] = np.where(
        gdf.countcat > 1, 2, gdf.fcat
    )

    fdf = pd.DataFrame({
        'existcae' : gdf.groupby(["a_cat"])['fcat'].agg('min')
    }).reset_index()

    polydf["cat"] = polydf.index + 1

    polydf = polydf.merge(fdf, how='left', left_on="cat", right_on="a_cat")

    polydf.rename(columns={
        'cat' : 'id_obj', lulccls_col : 'classuos'
    }, inplace=True)

    polydf['fonte']    = source
    polydf['classuos'] = polydf.classuos.astype(str)
    polydf['existcae'] = polydf.existcae.fillna(value=-1)
    polydf['existcae'] = polydf.existcae.astype(int)
    polydf['areaha']   = polydf.geometry.area / 10000

    polydf.drop(['a_cat'], axis=1, inplace=True)

    df_to_shp(polydf, oshp)

    return oshp


def thrd_caevs(tid, reffld, caefld, polyfld, lulccls, df, of, src):
    """
    cae_vs_polygon thread function
    """

    gws = mkdir(os.path.join(of, f'thrd_{str(tid)}'))

    for i, row in df.iterrows():

        cae_vs_polygon(
            os.path.join(caefld, row.caeshp),
            os.path.join(polyfld, row.polyshp),
            lulccls,
            os.path.join(reffld, row.refshp),
            os.path.join(of, f"caevs{src}_{str(row.refid)}.shp"),
            src,
            polycae=os.path.join(of, f"ivs{src}_{str(row.refid)}.shp"),
            ws=gws,
            loc=None
        )


def caevs_multiproc(reffolder, caefolder, polfolder, lulccls, source, ofolder):
    """
    Run cae_vs_polygon on a multi thread approach
    """

    import multiprocessing as mp
    import pandas as pd
    import datetime as dt

    from glass.pys.oss  import cpu_cores, lst_ff
    from glass.pd.split import df_split
    from glass.wt.js    import dict_to_json

    now = dt.datetime.utcnow().replace(microsecond=0)
    nowstr = now.strftime('%Y%m%d%H%M%S')

    logf = os.path.join(ofolder, f"log_{nowstr}.json")

    lmtdf = pd.DataFrame([{
        'refid'  : int(f.split('.')[0].split('_')[-1]),
        'refshp' : f
    } for f in lst_ff(
        reffolder, rfilename=True, file_format='.shp'
    )])

    caedf = pd.DataFrame([{
        'caeid'  : int(f.split('.')[0].split('_')[-1]),
        'caeshp' : f
    } for f in lst_ff(
        caefolder, rfilename=True, file_format='.shp'
    )])

    polydf = pd.DataFrame([{
        'polyid' : int(f.split('.')[0].split('_')[-1]),
        'polyshp' : f
    } for f in lst_ff(
        polfolder, rfilename=True, file_format='.shp'
    )])

    refdf = lmtdf.merge(caedf, how="outer", left_on="refid", right_on="caeid")
    refdf = refdf.merge(polydf, how="outer", left_on="refid", right_on="polyid")

    refdf = refdf[~refdf.refshp.isna()]
    refdf = refdf[~refdf.polyid.isna()]
    refdf = refdf[~refdf.caeid.isna()]

    # Get CPU Numbers
    n_cpu = cpu_cores()

    # Split data by CPU
    dfs = df_split(refdf, n_cpu)

    thrds = [mp.Process(
        target=thrd_caevs, name=f'th-{str(i+1)}',
        args=(i+1, reffolder, caefolder, polfolder, lulccls,
        dfs[i], ofolder, source)
    ) for i in range(len(dfs))]

    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    end = dt.datetime.utcnow().replace(microsecond=0)
    nowstr = now.strftime('%Y-%-m-%d %H:%M:%S')
    endstr = end.strftime('%Y-%-m-%d %H:%M:%S')

    logd = {
        "Status" : "OK",
        "START TIME" : nowstr,
        "END TIME" : endstr
    }

    dict_to_json(logd, logf)
    
    return ofolder

