"""
Columns to Rows
"""

def cols_to_rows(intbl, pk, colstoval, colstovalname, valcol, outtbl, sheet=None):
    """
    df_cols_to_rows_smp using data in files
    """

    from glass.rd import tbl_to_obj
    from glass.pd.dagg import df_cols_to_rows_smp
    from glass.wt import obj_to_tbl

    tdf = tbl_to_obj(intbl, sheet=sheet)

    ndf = df_cols_to_rows_smp(tdf, pk, colstoval, colstovalname, valcol)

    obj_to_tbl(ndf, outtbl)

    return outtbl

