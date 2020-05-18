"""
Aggreation tools
"""


def df_groupBy(df, grpCols, STAT=None, STAT_FIELD=None):
    """
    Group By Pandas Dataframe
    
    STAT OPTIONS:
    * MIN
    * MAX
    """
    
    from glass.pyt import obj_to_lst
    
    grpCols = obj_to_lst(grpCols)
    
    if not grpCols:
        raise ValueError("grpCols value is not valid")
    
    if not STAT:
        newDf = df.groupby(grpCols, axis=0, as_index=False)
    
    else:
        if not STAT_FIELD:
            raise ValueError("To use STAT, you must specify STAT_FIELD")
        
        if STAT == 'MIN':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].min()
        
        elif STAT == 'MAX':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].max()
        
        elif STAT == 'SUM':
            newDf = df.groupby(
                grpCols, axis=0, as_index=False
            )[STAT_FIELD].sum()
        
        else:
            raise ValueError("{} is not a valid option".format(STAT))
    
    return newDf

