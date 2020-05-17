"""
Table processing
"""

def merge_tbls(folder, out_tbl, tbl_format='.dbf'):
    """
    Merge all tables in folder into one single table
    """

    from glass.pys.oss import lst_ff
    from glass.ng.rd   import tbl_to_obj
    from glass.ng.wt   import obj_to_tbl
    from glass.ng.pd   import merge_df

    tbls = lst_ff(folder, file_format=tbl_format)

    tbls_dfs = [tbl_to_obj(t) for t in tbls]

    out_df = merge_df(tbls_dfs)

    obj_to_tbl(out_df, out_tbl)

    return out_tbl
