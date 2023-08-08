"""
Columns to Rows
"""

from glass.rd import tbl_to_obj
from glass.wt import obj_to_tbl


def cols_to_rows(intbl, pk, colstoval, colstovalname, valcol, outtbl, sheet=None):
    """
    df_cols_to_rows_smp using data in files
    """
    
    from glass.pd.dagg import df_cols_to_rows_smp

    tdf = tbl_to_obj(intbl, sheet=sheet)

    ndf = df_cols_to_rows_smp(tdf, pk, colstoval, colstovalname, valcol)

    obj_to_tbl(ndf, outtbl)

    return outtbl


def lstval_to_rows(tbl, sheet, coltosplit, otbl, splitchar=';'):
    """
    List values to a new row

    tbl = './areainf_cs_2021.xlsx'
    sheet = 'Area_influencia'
    splitchar = ';'
    coltosplit = 'fregid'
    otbl = './areainf_cs_2021_v3.xlsx'
    """

    from glass.pd.dagg import col_list_val_to_row

    df = tbl_to_obj(tbl, sheet=sheet)

    df[coltosplit] = df[coltosplit].astype(str)

    df['lst'] = df[coltosplit].str.split(splitchar)

    ndf = col_list_val_to_row(df, 'lst')

    ndf.drop([coltosplit], axis=1, inplace=True)
    ndf.rename(columns={'lst' : coltosplit}, inplace=True)

    ndf = ndf[ndf[coltosplit] != '']

    obj_to_tbl(ndf, otbl)

    return otbl

