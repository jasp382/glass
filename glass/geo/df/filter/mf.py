"""
Apply several filters and save results in files 
"""

def exp_by_group_relfeat(shp, group_col, relfeat, relfeat_id,
    reltbl, reltbl_sheet, group_fk, relfeat_fk, out_folder, out_tbl):
    """
    Identify groups in shp, get features related with
    these groups and export group features and related
    features to new file
    """

    import os
    import pandas as pd
    from glass.dct           import tbl_to_obj, obj_to_tbl
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.dct.geo.toshp import obj_to_shp
    from glass.geo.prop.prj  import get_epsg_shp

    epsg = get_epsg_shp(shp)

    # Open data
    shp_df = shp_to_obj(shp)
    rel_df = shp_to_obj(relfeat)

    # Get table with relations N-N
    nn_tbl = tbl_to_obj(reltbl, sheet=reltbl_sheet)

    # Relate relfeat with shp groups
    rel_df = rel_df.merge(
        nn_tbl, how='inner',
        left_on=relfeat_id, right_on=relfeat_fk
    )

    # List Groups
    grp_df = pd.DataFrame({
        'cnttemp' : shp_df.groupby([group_col])[group_col].agg('count')
    }).reset_index()

    ntbls = []
    # Filter and export
    for idx, row in grp_df.iterrows():
        # Get shp_df filter
        new_shp = shp_df[shp_df[group_col] == row[group_col]]

        # Get relfeat filter
        new_relf = rel_df[rel_df[group_fk] == row[group_col]]

        # Export
        shp_i = obj_to_shp(new_shp, 'geometry', epsg, os.path.join(
            out_folder, 'lyr_{}.shp'.format(row[group_col])
        ))
        rel_i = obj_to_shp(new_relf, 'geometry', epsg, os.path.join(
            out_folder, 'rel_{}.shp'.format(row[group_col])
        ))

        ntbls.append([row[group_col], shp_i, rel_i])
    
    ntbls = pd.DataFrame(ntbls, columns=['group_id', 'shp_i', 'rel_i'])

    obj_to_tbl(ntbls, out_tbl)
    
    return out_tbl

