"""
Operations with ArcMap DataFrames
"""

import arcpy

def lst_dataframe(mxdObj, dfNames=None):
    """
    List Dataframes in a MXD Project
    """
    
    from glass.pys import obj_to_lst
    
    dfNames = obj_to_lst(dfNames)
    
    dfs = arcpy.mapping.ListDataFrames(mxdObj)
    
    if dfNames:
        dfObjs = [df for df in dfs if str(df.name) in dfNames]
    
    else:
        dfObjs = dfs
    
    if len(dfObjs) == 0:
        return None
    
    elif len(dfObjs) == 1:
        return dfObjs[0]
    
    else:
        return dfObjs

