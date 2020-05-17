"""
Join DF's
"""

def join_dfs(df_a, df_b, colA, colB, onlyCombinations=True):
    """
    Join two Pandas Dataframes
    """
    
    from glass.pys  import obj_to_lst
    
    _HOW_ = 'inner' if onlyCombinations else 'outer'
    
    if colA == 'index' and colB == 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_index=True, right_index=True
        )
    
    elif colA == 'index' and colB != 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_index=True,
            right_on=obj_to_lst(colB)
        )
    
    elif colA != 'index' and colB == 'index':
        newDf = df_a.merge(
            df_b, how=_HOW_, left_on=obj_to_lst(colA),
            right_index=True
        )
    
    else:
        newDf = df_a.merge(
            df_b, how=_HOW_, left_on=obj_to_lst(colA),
            right_on=obj_to_lst(colB)
        )
    
    return newDf


def sum_field_of_two_tables(df_one, join_field_one,
                            df_two, join_field_two,
                            field_to_sum):
    """
    Sum same field in different tables
    
    Table 1:
    id | field
    0 |  10
    1 |  11
    2 |  13
    3 |  10
    
    Table 2:
    id | field
    0 |  10
    1 |   9
    2 |  17
    4 |  15
    
    Create the new table
    id | field
    0 |  20
    1 |  20
    2 |  30
    3 |  10
    4 |  15
    """
    
    df_two.rename(columns={field_to_sum : 'sum_pro'}, inplace=True)
    
    if join_field_two == join_field_one:
        df_two.rename(columns={join_field_two : 'id_table_two'}, inplace=True)
        
        join_field_two = 'id_table_two'
    
    result = df_one.merge(
        df_two, how='outer', left_on=join_field_one, right_on=join_field_two
    )
    
    result.fillna(0, inplace=True)
    
    result[field_to_sum] = result[field_to_sum] + result['sum_pro']
    
    result[join_field_one].replace(0, result[join_field_two], inplace=True)
    
    result.drop(join_field_two, axis=1, inplace=True)
    result.drop('sum_pro', axis=1, inplace=True)
    
    return result


def combine_dfs(mainDf, joinDfs, int_col):
    """
    Join two tables using a interest column with the same name in both
    dataframes and return a new table with the result
    """
    
    joinDfs = [joinDfs] if type(joinDfs) != list else joinDfs
    join_field = 'id_entity'
    
    for jdf in joinDfs:
        jdf.rename(columns={int_col : join_field}, inplace=True)
    
        mainDf = mainDf.merge(
            jdf, how='outer',
            left_on=int_col, right_on=join_field
        )
        
        mainDf.fillna(0, inplace=True)
        
        mainDf[int_col].replace(0, mainDf[join_field], inplace=True)
        
        mainDf.drop(join_field, axis=1, inplace=True)
    
    return mainDf

