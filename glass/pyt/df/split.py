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
