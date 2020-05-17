"""
Extract data from DATABASE
"""


def distinct_val(db, pgtable, column):
    """
    Get distinct values in one column of one pgtable
    """
    
    from glass.pyt    import obj_to_lst
    from glass.sql.fm import q_to_obj
    
    data = q_to_obj(db,
        "SELECT {col} FROM {t} GROUP BY {col};".format(
            col=", ".join(obj_to_lst(column)), t=pgtable
        ), db_api='psql'
    ).to_dict(orient="records")
    
    return data


def run_query_for_values_in_col(db, query,
                               table_interest_col, interest_col,
                               outworkspace):
    """
    Execute a query for each value in one column
    In each iteration, the values may participate in the query.
    
    Export the several tables to excel
    
    Example:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM
        0       |   255   |'2018-01-01 | xxxx
        0       |   255   |'2018-01-01 | xxxx
        0       |   254   |'2018-01-01 | xxxx
        0       |   254   |'2018-01-01 | xxxx
        0       |   255   |'2018-01-02 | xxxx
        0       |   255   |'2018-01-02 | xxxx
        0       |   254   |'2018-01-02 | xxxx
        0       |   254   |'2018-01-02 | xxxx
    
    For a query as:
    SELECT ID_PERCURSO, PARAGEM, GEOM, DIA, COUNT(PARAGEM) AS conta FROM
    table WHERE DIA={} GROUP BY PARAGEM, GEOM, DIA;
    
    This method will generate two tables:
    First table:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM | conta
         0     |   255   |'2018-01-01 | xxxx |   2
         0     |   254   |'2018-01-01 | xxxx |   2
    
    Second table:
    ID_PERCURSO | PARAGEM |    DIA     | GEOM | conta
          0     |   255   |'2018-01-02 | xxxx |   2
          0     |   254   |'2018-01-02 | xxxx |   2
    
    {} will be replaced for every value in the interest_column that will
    be iterated one by one
    """
    
    import os
    from glass.sql.fm import q_to_obj
    from glass.sql.i  import cols_type
    from glass.dct.to import obj_to_tbl
    
    fields_types = cols_type(db, table_interest_col)
    
    # Get  unique values
    VALUES = q_to_obj(db,
        "SELECT {col} FROM {t} GROUP BY {col}".format(
            col=interest_col, t=table_interest_col
        ), db_api='psql'
    )[interest_col].tolist()
    
    # Aplly query for every value in VALUES
    # Write data in excel
    for value in VALUES:
        data = q_to_obj(db, query.format(
            str(value[0]) if fields_types[interest_col] != str else \
            "'{}'".format(str(value[0]))
        ), db_api='psql')
        
        obj_to_tbl(data, os.path.join(outworkspace, '{}_{}.xlsx'.format(
            table_interest_col, str(value[0])
        )))


def rows_notin_q(db, tblA, tblB, joinCols, newTable,
                 cols_to_mantain=None, tblAisQuery=None,
                 tblBisQuery=None):
    """
    Get rows from tblA that are not present in tblB
    
    joinCols = {colTblA : colTblB}
    """
    
    from glass.pyt    import obj_to_lst
    from glass.sql.to import q_to_ntbl
    
    cols_to_mantain = obj_to_lst(cols_to_mantain)
    
    q = (
        "SELECT {cls} FROM {ta} LEFT JOIN {tb} ON "
        "{rel} WHERE {tblB}.{fldB} IS NULL"
    ).format(
        cls=cols_to_mantain if cols_to_mantain else "{}.*".format(tblA),
        ta=tblA if not tblAisQuery else tblAisQuery,
        tb=tblB if not tblBisQuery else tblBisQuery,
        rel=" AND ".join(["{ta}.{ca} = {tb}.{cb}".format(
            ta=tblA, tb=tblB, ca=k, cb=joinCols[k]
        ) for k in joinCols])
    )
    
    newTable = q_to_ntbl(db, newTable, q, api='psql')
    
    return newTable
