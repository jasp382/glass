"""
Columns Operations inside Pandas Dataframes
"""

import pandas as pd

def fld_types(df):
    """
    Return Columns Types
    """
    
    t = dict(df.dtypes)
    
    return {c : str(t[c]) for c in t}


def col_distinct(df, col):
    """
    Get Distinct Values in a Column of a Pandas Dataframe
    """
    
    return list(df[col].unique())


def del_cols_notin_ref(df, flds, geomCol=None):
    """
    Delete columns not in flds
    """
    
    from glass.pys import obj_to_lst
    
    cols  = df.columns.values
    
    F_GEOM = None
    if not geomCol:
        for c in cols:
            if c == 'geometry' or c == 'geom':
                F_GEOM = c
                break
    else:
        F_GEOM = geomCol
        
    if not flds and not F_GEOM:
        return df
    
    elif not flds and F_GEOM:
        Icols = [F_GEOM]
        
    elif flds and F_GEOM:
        Icols = obj_to_lst(flds) + [F_GEOM]
    
    else:
        Icols = obj_to_lst(flds)
    
    DEL_COLS = [c for c in cols if c not in Icols]
    
    df.drop(DEL_COLS, axis=1, inplace=True)
    
    return df


def distinct_of_distinct(df, colMain, colTwo):
    """
    List a distinct values in one column and for each value
    see the distinct values in other column
    """
    
    keys = col_distinct(df, colMain)
    
    d = {}
    for k in keys:
        __df = df[df[colMain] == k]
        
        val = col_distinct(__df, colTwo)
        
        d[k] = val
    
    return d


def listval_to_newcols(df, listColumn):
    """
    List values on column to new column
    """
    
    import pandas
    
    newDf = pandas.concat([
        df.drop([listColumn], axis=1),
        df[listColumn].apply(pandas.Series)
    ], axis=1)
    
    return newDf


def splitcol_to_newcols(df, col, sep, newCols):
    """
    Split String Column into several columns
    """
    
    df["lst"] = df[col].str.split(sep)
    
    newDf = listval_to_newcols(df, "lst")
    
    newDf.rename(columns=newCols, inplace=True)
    
    return newDf


def dictval_to_cols(df, dictcol):
    """
    DataFrame like:

       A                 B
    0  {'a': 3}          6
    1  {'b': 4, 'c': 5}  7

    Will became like this:
       A                 B   a    b    c
    0  {'a': 3}          6   3.0  NaN  NaN
    1  {'b': 4, 'c': 5}  7   NaN  4.0  5.0
    """

    ndf = pd.concat([
        df, df[dictcol].apply(pd.Series)
    ], axis=1)

    return ndf

