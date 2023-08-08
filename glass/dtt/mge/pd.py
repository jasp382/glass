import pandas as pd


def merge_df(dfs, ignIndex=True, ignoredfstype=None):
    """
    Merge Multiple DataFrames into one
    """
    
    if type(dfs) != list and not ignoredfstype:
        raise ValueError('dfs should be a list with Pandas Dataframe')
    
    result = pd.concat(dfs, ignore_index=ignIndex)
    
    return result
