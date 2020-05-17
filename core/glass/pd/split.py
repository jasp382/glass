"""
Split Pandas DataFrame
"""


def df_split(df, ndf, nrows=None):
    """
    Split Dataframe in several

    if not nrows:
        Split df in several dataframe in number equal to ndf
    else:
        Split Dataframe making each sub dataframe having only
        ndf rows
    """

    import numpy as npdf

    if nrows:
        __ndf = df.shape[0] / ndf
        ndf = __ndf if int(__ndf) == __ndf else int(__ndf) + 1

    dfs = npdf.array_split(df, ndf)

    return dfs


def df_split_by_attrval(df, attr):
    """
    Split df by each value in column
    """

    values = df[attr].unique()

    new_dfs = []
    for v in values:
        new_df = df[df[attr] == v]

        new_dfs.append(new_df)
    
    return new_dfs

