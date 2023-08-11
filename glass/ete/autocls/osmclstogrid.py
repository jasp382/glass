"""
Produce Ref GRID from OSM2LULC results
"""

import os
import pandas          as pd
import multiprocessing as mp
from glass.pys.oss     import mkdir, fprop


def lulc_by_cell(tid, boundary, lulc_shps, fishnet, result, workspace):
    from glass.wenv.grs import run_grass
    from glass.dtt.torst import shp_to_rst

    bname = fprop(boundary, 'fn')
    # Boundary to Raster
    ref_rst = shp_to_rst(
        boundary, None, 10, 0, os.path.join(
            workspace, f'rst_{bname}.tif'
        )
    )
    
    # Create GRASS GIS Session
    loc_name = 'loc_' + bname
    gbase = run_grass(workspace, location=loc_name, srs=ref_rst)
    
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, workspace, loc_name, 'PERMANENT')
    
    # GRASS GIS Modules
    from glass.it.shp    import shp_to_grs, grs_to_shp
    from glass.gp.ovl    import grsintersection
    from glass.tbl.attr  import geomattr_to_db
    from glass.prop.feat import feat_count
    
    # Send Fishnet to GRASS GIS
    fnet = shp_to_grs(fishnet, fprop(fishnet, 'fn'), asCMD=True)

    # Processing
    ulst = []
    l_lulc_grs = []
    for shp in lulc_shps:
        iname = fprop(shp, 'fn')

        # LULC Class to GRASS GIS
        lulc_grs = shp_to_grs(shp, iname, filterByReg=True, asCMD=True)

        if not feat_count(lulc_grs, gisApi='grass', work=workspace, loc=loc_name):
            continue
        
        # Intersect Fishnet | LULC CLass
        union_grs = grsintersection(
            fnet, lulc_grs, iname + '_i', cmd=True)
        
        # Get Areas
        geomattr_to_db(union_grs, "areav", "area", "boundary", unit='meters')

        # Export Table
        funion = grs_to_shp(
            union_grs, os.path.join(result, iname + '.shp'), 'area'
        )

        ulst.append(funion)
        l_lulc_grs.append(lulc_grs)
    
    # Intersect between all LULC SHPS
    ist_shp = []
    if len(l_lulc_grs) > 1:
        for i in range(len(l_lulc_grs)):
            for e in range(i+1, len(l_lulc_grs)):
                ishp = grsintersection(
                    l_lulc_grs[i], l_lulc_grs[e],
                    'lulcint_' + str(i) + '_' + str(e),
                    cmd=True
                )
                
                if not feat_count(ishp, gisApi='grass', work=workspace, loc=loc_name):
                    continue
                else:
                    ist_shp.append(ishp)
        
        if len(ist_shp):
            from glass.gp.gen import dissolve
            from glass.tbl.grs import reset_table

            if len(ist_shp) > 1:
                from glass.dtt.mge import shps_to_shp

                # Export shapes
                _ist_shp = [grs_to_shp(s, os.path.join(
                    workspace, loc_name, s + '.shp'), 'area') for s in ist_shp]
                
                # Merge Intersections
                merge_shp = shps_to_shp(_ist_shp, os.path.join(
                    workspace, loc_name, 'merge_shp.shp'), api='pandas')
                
                # Import GRASS
                merge_shp = shp_to_grs(merge_shp, 'merge_shp')
            
            else:
                merge_shp = ist_shp[0]
            
            # Dissolve Shape
            reset_table(merge_shp, {'refid' : 'varchar(2)'}, {'refid' : '1'})
            overlay_areas = dissolve(merge_shp, 'overlay_areas', 'refid', api='grass')

            # Union Fishnet | Overlay's
            union_ovl = grsintersection(fnet, overlay_areas, 'ovl_union', cmd=True)

            funion_ovl = grs_to_shp(
                union_ovl, os.path.join(result, union_ovl + '.shp'), 'area'
            )

            ulst.append(funion_ovl)
    
    # Export Tables
    return ulst


def thrd_lulc_by_cell(thrd_id, df_fishnet, l_lulc, result):
    # Create folder for this thread
    t_folder = mkdir(os.path.join(result, 'thrd_' + str(thrd_id)))
    
    # For each fishnet, do the job
    for idx, row in df_fishnet.iterrows():
        rf = mkdir(os.path.join(result, fprop(row.fishnet, 'fn')))

        lulc_by_cell(int(idx), row.bound, l_lulc, row.fishnet, rf, t_folder)


def osmlulc_to_s2grid(ref_raster, osmtolulc, lucol, tmp_folder, results):
    """
    OSM LULC to Sentinel-2 GRID
    """

    from glass.smp.fish import nfishnet_fm_rst
    from glass.pys.oss  import lst_ff, cpu_cores
    from glass.wt       import obj_to_tbl
    from glass.pd.split import df_split
    from glass.rd.shp   import shp_to_obj
    from glass.wt.shp   import df_to_shp, shpext_to_boundshp

    # Create Fishnets
    fishnets = mkdir(os.path.join(tmp_folder, 'fishnets_shp'))
    fnet= nfishnet_fm_rst(ref_raster, 500 , 500, fishnets)

    # List Fishnet
    df_fnet = pd.DataFrame(fnet, columns=['fishnet'])

    # List results
    lst_lulc = lst_ff(osmtolulc, file_format='.shp')

    # Produce boundaries for each fishnet
    bf = mkdir(os.path.join(tmp_folder, 'boundaries'))

    def produce_bound(row):
        row['bound'] = shpext_to_boundshp(
            row.fishnet, os.path.join(bf, os.path.basename(row.fishnet))
        )

        return row

    df_fnet = df_fnet.apply(lambda x: produce_bound(x), axis=1)
    df_fnet['idx'] = df_fnet.index

    # Get CPU Numbers
    n_cpu = cpu_cores()

    # Split data by CPU
    dfs = df_split(df_fnet, n_cpu)

    thrds = [mp.Process(
        target=thrd_lulc_by_cell, name='th_{}'.format(str(i+1)),
        args=(i+1, dfs[i], lst_lulc, tmp_folder)
    ) for i in range(len(dfs))]

    for i in thrds:
        i.start()
    
    for i in thrds:
        i.join()
    
    # Re-list fishnets
    fish_files = df_fnet.fishnet.tolist()

    for fishp in fish_files:
        # List Intersection files for each fishnet
        int_files = lst_ff(os.path.join(
            tmp_folder, fprop(fishp, 'fn')
        ), file_format='.shp')

        if not len(int_files):
            continue
        
        # Open Fishnet
        fish_df = shp_to_obj(fishp)
        fish_df.rename(columns={'FID' : 'fid'}, inplace=True)
        fish_df['area'] = fish_df.geometry.area

        # Open other files
        for f in int_files:
            fn = fprop(f, 'fn')

            df = shp_to_obj(f)

            if fn != 'ovl_union':
                df = df[~df['b_' + lucol].isnull()]
                clsid = df['b_' + lucol].unique()[0]
            else:
                df = df[~df.b_refid.isnull()]
                clsid = None
            
            if fn == 'ovl_union':
                df['areav'] = df.geometry.area
            
            df = pd.DataFrame({'areav' : df.groupby(['a_FID'])['areav'].agg('sum')}).reset_index()

            fish_df = fish_df.merge(df, how='left', left_on='fid', right_on='a_FID')

            if fn != 'ovl_union':
                fish_df['lu_' + str(clsid)] = fish_df.areav * 100 / fish_df.area
            
            else:
                fish_df['overlay'] = fish_df.areav * 100 / fish_df.area
            
            fish_df.drop(['areav', 'a_FID'], axis=1, inplace=True)
        
        # Save file
        df_to_shp(fish_df, os.path.join(results, os.path.basename(fishp)))
    
    # Write List of Fishnet
    obj_to_tbl(df_fnet, os.path.join(results, 'fishnet_list.xlsx'))

    return results

