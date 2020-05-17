"""
Manage data in Pandas DataFrame
"""


def col_list_val_to_row(pndDf, colWithLists, geomCol=None, epsg=None):
    """
    Convert a dataframe:
    
       | col_a | col_b | col_c
     0 |   X   |   X   |   1
     1 |   X   |   X   | [2,3]
     
    To:
       | col_a | col_b | col_c
     0 |   X   |   X   |   1
     1 |   X   |   X   |   2
     2 |   X   |   X   |   3
    """
    
    def desmembrate(row, row_acc, target_col):
        if type(row[target_col]) != list:
            row_acc.append(row.to_dict())
        
        else:
            for geom in row[target_col]:
                new_row = row.to_dict()
                new_row[target_col] = geom
                row_acc.append(new_row)
    
    new_rows = []
    pndDf.apply(lambda x: desmembrate(
        x, new_rows, colWithLists), axis=1
    )
    
    # Convert again to DataFrame
    if geomCol and epsg:
        from glass.geo.obj.pd import df_to_geodf
        
        return df_to_geodf(new_rows, geomCol, epsg)
    
    else:
        import pandas
        
        return pandas.DataFrame(new_rows)


def dfcolstorows(inDf, colField, valField, colFid=None):
    """
    Dataframe Like:
    
      | pop_res |   ind2  | ind3 | id_unit
    0 |   571   | 35.0975 | 123  |  3768 
    1 |   938   | 18.2114 | 265  |  3618 
    2 |   554   | 44.3149 |  76  |  3788 
    3 |   711   | 37.8619 | 134  |  3766
    4 |  1268   | 46.0733 | 203  |  3690
    
    To:
    
      | colField | valField
    0 | pop_res |   571
    1 |  ind2   | 35.0975
    2 |  ind3   |   123
    3 | id_unit |  3768 
    4 | pop_res | 938
    5 |  ind2   | 18.2114
    6 |  ind3   | 265
    7 | id_unit | 3618
    """

    from glass.dp.pd import merge_df
    
    newDfs = []
    cols = list(inDf.columns.values)
    
    if colFid and colFid in cols:
        cols.remove(colFid)
    
    for col in cols:
        ndf = inDf.copy()
        
        ndf.drop([c for c in cols if c != col], axis=1, inplace=True)
        ndf[colField] = col
        ndf.rename(columns={col : valField}, inplace=True)
        
        newDfs.append(ndf)
    
    res = merge_df(newDfs)
    
    return res


def df_cols_to_rows(inDf, TO_COLS, col_old_col_name, key_old_col_name, col_mantain):
    """
    Dataframe like:

      | pop_res |   ind2  | ind3 |  ind5   | id_unit |pop_res_int | ind2_int | ind3_int| ind5_int
    0 |   571   | 35.0975 | 123  | 97.373  |   3768  |     2      |    6     |    2    |    7
    1 |   938   | 18.2114 | 265  | 93.4968 |   3618  |     3      |    1     |    5    |    4
    2 |   554   | 44.3149 |  76  | 97.4074 |   3788  |     1      |    7     |    1    |    7
    3 |   711   | 37.8619 | 134  | 96.1429 |   3766  |     2      |    6     |    3    |    6
    4 |  1268   | 46.0733 | 203  | 90.9385 |   3690  |     5      |    7     |    4    |    3

    To:

    0 | id_unit | id_indicator |  value  | cls
    2 |   3768  |    pop_res   |   571   |  2
    3 |   3768  |     ind2     | 35.0975 |  6
    4 |   3768  |     ind3     |   123   |  2
    5 |   3768  |     ind5     | 97.373  |  7
    6 |   3618  |    pop_res   |   938   |  3
    7 |   3618  |     ind2     | 18.2114 |  1
    8 |   3618  |     ind3     |   265   |  5 
    9 |   3618  |     ind5     | 93.4968 |  4
    ...
    
    Using as parameters:
    data_cols = ['pop_res', 'ind2', 'ind3', 'ind5']
    col_mantain = 'id_unit'
    TO_COLS = {
        # Dict values should have the same length
        'value' : data_cols,
        'cls'   : [i + '_int' for i in data_cols]
    }
    
    col_old_col_name = 'id_indicator'
    key_old_col_name = 'value'
    """
    
    from glass.pys  import obj_to_lst
    
    col_mantain = obj_to_lst(col_mantain)
    newCols     = list(TO_COLS.keys())
    newDfs      = []
    
    for i in range(len(TO_COLS[newCols[0]])):
        ndf = inDf.copy(deep=True)
        
        DROP_COLS = []
        COLS_MANT = col_mantain.copy()
        
        for K in TO_COLS:
            COLS_MANT.append(TO_COLS[K][i])
        
        for col in ndf.columns.values:
            if col not in COLS_MANT:
                DROP_COLS.append(col)
        
        ndf.drop(DROP_COLS, axis=1, inplace=True)
        ndf.rename(columns={TO_COLS[k][i] : k for k in TO_COLS}, inplace=True)
        
        ndf[col_old_col_name] = TO_COLS[key_old_col_name][i]
        
        newDfs.append(ndf)
    
    outDf = merge_df(newDfs)
    
    return outDf

