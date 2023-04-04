"""
Compare tables Shape (number of columns and rows)
"""

import os
import pandas as pd


def foldertbls_have_samerows(mfolder, tbl_a, tbl_b, out):
    """
    For each folder in mfolder, see if tbl_a and tbl_b
    have the same number of rows
    """

    return out


def tblsameid_have_samerows(fa, fb, faff, fbff, out):
    """
    Count number of rows in several Tables with the same
    ID in the file name
    """

    from glass.pys.oss import lst_ff
    from glass.prop    import is_shp
    from glass.rd      import tbl_to_obj
    from glass.rd.shp  import shp_to_obj
    from glass.wt      import obj_to_tbl

    # Get Files by id
    a_tbl = pd.DataFrame([{
        'aid'  : int(f.split('.')[0].split('_')[-1]),
        'atbl' : f
    } for f in lst_ff(
        fa, rfilename=True, file_format=faff
    )])

    # List tables in folder b
    b_tbl = pd.DataFrame([{
        'bid'  : int(f.split('.')[0].split('_')[-1]),
        'btbl' : f
    } for f in lst_ff(
        fb, rfilename=True, file_format=fbff
    )])

    # Join two dataframes
    jt = a_tbl.merge(b_tbl, how='inner', left_on='aid', right_on='bid')

    # Check number of rows of each table
    # Record result
    res = []
    for i, r in jt.iterrows():
        # Check if table is geo or not
        shpa = os.path.join(fa, r.atbl)
        shpb = os.path.join(fb, r.btbl)
    
        a_is_shp = is_shp(shpa)
        b_is_shp = is_shp(shpb)
    
        # Open Tables
        dfa = shp_to_obj(shpa) if a_is_shp else tbl_to_obj(shpa)
        dfb = shp_to_obj(shpb) if b_is_shp else tbl_to_obj(shpb)
    
        # Get row number
        row_a = dfa.shape[0]
        row_b = dfb.shape[0]
    
        # Write result
        res.append([
            os.path.basename(shpa), os.path.basename(shpb),
            row_a, row_b, 1 if row_a == row_b else 0
        ])
    
    # Export result to file
    res_df = pd.DataFrame(
        res, columns=["shpa", "shpb", "ta_rows", "tb_rows", "status"])

    obj_to_tbl(res_df, out)

    return out

