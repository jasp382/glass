"""
Fields Operations inside Pandas Dataframes
"""

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


def del_fld_notin_geodf(df, flds, geomCol=None):
    """
    Delete columns not in flds
    """
    
    from glass.pyt import obj_to_lst
    
    cols  = df.columns.values
    
    if not geomCol:
        for c in cols:
            if c == 'geometry' or c == 'geom':
                F_GEOM = c
                break
    else:
        F_GEOM = geomCol
        
    if not flds:
        Icols = [F_GEOM]
        
    else:
        Icols = obj_to_lst(flds) + [F_GEOM]
    
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

