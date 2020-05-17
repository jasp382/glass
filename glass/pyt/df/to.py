"""
Python Object To Python Object
"""

def df_to_dict(df, colsIsIndex=None, valueIsList=None):
    """
    Pandas Dataframe to Dict
    """
    
    if not colsIsIndex:
        if not valueIsList:
            return df.to_dict(orient="index")
        else:
            return df.T.to_dict(orient="list")
    
    else:
        return df.to_dict(orient="list")


def df_to_list(df):
    """
    Pandas Dataframe to List Like Array with dicts as values
    """
    
    return df.to_dict(orient="records")


def series_to_list(pndS):
    """
    Pandas series to List
    """
    
    return pndS.tolist()


def dict_to_df(df):
    """
    Dict to index
    """
    
    import pandas
    
    return pandas.DataFrame.from_dict(df, orient="index")


def merge_df(dfs, ignIndex=True):
    """
    Merge Multiple DataFrames into one
    """
    
    if type(dfs) != list:
        raise ValueError('dfs should be a list with Pandas Dataframe')
    
    result = dfs[0]
    
    for df in dfs[1:]:
        result = result.append(df, ignore_index=ignIndex)#, sort=True)
    
    return result

