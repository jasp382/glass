"""
Manage DBMS Tables
"""

def create_tbl(db, table, fields, orderFields=None, api='psql'):
    """
    Create Table in Database
    
    API's Available:
    * psql;
    * sqlite;
    """
    
    if api == 'psql':
        from glass.sql.c import sqlcon
    
        ordenedFields = orderFields if orderFields else fields.keys()
    
        con = sqlcon(db)
    
        cursor = con.cursor()
    
        cursor.execute("CREATE TABLE {} ({})".format(
            table, ', '.join(['{} {}'.format(
                ordenedFields[x], fields[ordenedFields[x]]
            ) for x in range(len(ordenedFields))])
        ))
    
        con.commit()
    
        cursor.close()
        con.close()
    
    elif api == 'sqlite':
        import sqlite3
        
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        cursor.execute("CREATE TABLE {} ({})".format(
            table, ', '.join(["{} {}".format(
                k, fields[k]) for k in fields])
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    return table


def new_view(sqliteDb, newView, q):
    """
    Create view in a SQLITE DB
    """

    import sqlite3
    
    conn = sqlite3.connect(sqliteDb)
    cs = conn.cursor()
    
    cs.execute("CREATE VIEW {} AS {}".format(newView, q))
    
    conn.commit()
    cs.close()
    conn.close()
    
    return newView


def rename_tbl(db, tblNames):
    """
    Rename PGSQL Table
    
    tblNames = {old_name: new_name, ...}
    """
    
    from glass.sql.c import sqlcon
    
    con = sqlcon(db)
    
    cursor = con.cursor()
    
    new_names =[]
    for k in tblNames:
        cursor.execute(
            "ALTER TABLE {} RENAME TO {}".format(k, tblNames[k])
        )
        new_names.append(tblNames[k])
    
    con.commit()
    
    cursor.close()
    con.close()
    
    return new_names[0] if len(new_names) == 1 else new_names


"""
Delete Tables
"""

def del_tables(db, pg_table_s, isViews=None, isBasename=None, db_set='default'):
    """
    Delete all tables in pg_table_s
    """
    
    from glass.pys    import obj_to_lst
    from glass.sql.c import sqlcon
    
    pg_table_s = obj_to_lst(pg_table_s)
    
    if isBasename:
        if not isViews:
            from glass.prop.sql import lst_tbl
        
            pg_table_s = lst_tbl(db, api='psql', basename=pg_table_s, db_set=db_set)
        else:
            from glass.prop.sql import lst_views
            
            pg_table_s = lst_views(db, basename=pg_table_s, dbset=db_set)
        
    con = sqlcon(db, dbset=db_set)
    
    l = []
    for i in range(0, len(pg_table_s), 100):
        l.append(pg_table_s[i:i+100])
    
    for lt in l:
        cursor = con.cursor()
        cursor.execute('DROP {} IF EXISTS {};'.format(
            'TABLE' if not isViews else 'VIEW', ', '.join(lt)))
        con.commit()
        cursor.close()
    
    con.close()


def drop_tbldata(db, table, where=None, dbset='default'):
    """
    Delete all data on a PGSQL Table
    """
    
    from glass.sql.c import sqlcon
    
    con = sqlcon(db, dbset=dbset)
    
    cursor = con.cursor()    
    
    cursor.execute("DELETE FROM {}{};".format(
        table, "" if not where else " WHERE {}".format(where)
    ))
    
    con.commit()
    cursor.close()
    con.close()


def drop_where_cols_are_same(db, table, colA, colB):
    """
    Delete rows Where colA has the same value than colB
    """
    
    from glass.sql.c import sqlcon
    
    con = sqlcon(db)
    
    cursor = con.cursor()
    
    cursor.execute('DELETE FROM {} WHERE {}={}'.format(table, colA, colB))
    
    con.commit()
    cursor.close()
    con.close()

"""
Write new tables or edit tables in Database
"""


def update_table(db, pg_table, dic_new_values, dic_ref_values=None, 
                 logic_operator='OR'):
    """
    Update Values on a PostgreSQL table

    new_values and ref_values are dict with fields as keys and values as 
    keys values.
    If the values (ref and new) are strings, they must be inside ''
    e.g.
    dic_new_values = {field: '\'value\''}
    """
    
    from glass.sql.c import sqlcon

    __logic_operator = ' OR ' if logic_operator == 'OR' else ' AND ' \
        if logic_operator == 'AND' else None

    if not __logic_operator:
        raise ValueError((
            'Defined operator is not valid.\n '
            'The valid options are \'OR\' and \'AND\'')
        )

    con = sqlcon(db)

    cursor = con.cursor()
    
    if dic_ref_values:
        whrLst = []
        for x in dic_ref_values:
            if dic_ref_values[x] == 'NULL':
                whrLst.append('{} IS NULL'.format(x))
            else:
                whrLst.append('{}={}'.format(x, dic_ref_values[x]))
        
        whr = " WHERE {}".format(__logic_operator.join(whrLst))
    
    else:
        whr = ""

    update_query = "UPDATE {tbl} SET {pair_new}{where};".format(
        tbl=pg_table,
        pair_new=",".join(["{fld}={v}".format(
            fld=x, v=dic_new_values[x]) for x in dic_new_values]),
        where = whr
    )

    cursor.execute(update_query)

    con.commit()
    cursor.close()
    con.close()


def update_query(db, table, new_values, wherePairs, whrLogic="OR"):
    """
    Update SQLITE Table
    """
    
    import sqlite3
    
    conn = sqlite3.connect(db)
    cs   = conn.cursor()
    
    LOGIC_OPERATOR = " OR " if whrLogic == "OR" else " AND " \
        if whrLogic == "AND" else None
    
    if not LOGIC_OPERATOR:
        raise ValueError("whrLogic value is not valid")
    
    Q = "UPDATE {} SET {} WHERE {}".format(
        table, ", ".join(["{}={}".format(
            k, new_values[k]) for k in new_values
        ]),
        LOGIC_OPERATOR.join(["{}={}".format(
            k, wherePairs[k]) for k in wherePairs
        ])
    )
    
    cs.execute(Q)
    
    conn.commit()
    cs.close()
    conn.close()
    

def set_values_use_pndref(sqliteDB, table, colToUpdate,
                        pndDf, valCol, whrCol, newCol=None):
    """
    Update Column based on conditions
    
    Add distinct values in pndCol in sqliteCol using other column as Where
    """
    
    import sqlite3
    
    conn = sqlite3.connect(sqliteDB)
    cs   = conn.cursor()
    
    if newCol:
        cs.execute("ALTER TABLE {} ADD COLUMN {} integer".format(
            table, colToUpdate
        ))
    
    VALUES = pndDf[valCol].unique()
    
    for val in VALUES:
        filterDf = pndDf[pndDf[valCol] == val]
        
        cs.execute("UPDATE {} SET {}={} WHERE {}".format(
            table, colToUpdate, val,
            str(filterDf[whrCol].str.cat(sep=" OR "))
        ))
    
    conn.commit()
    cs.close()
    conn.close()


def replace_null_with_other_col_value(db, pgtable, nullFld, replaceFld):
    """
    Do the following
    
    Convert the next table:
    FID | COL1 | COL2
     0  |  1   | -99
     1  |  2   | -99
     2  | NULL | -88
     3  | NULL | -87
     4  |  7   | -99
     5  |  9   | -99
     
    Into:
    FID | COL1 | COL2
     0  |  1   | -99
     1  |  2   | -99
     2  | -88  | -88
     3  | -87  | -87
     4  |  7   | -99
     5  |  9   | -99
    """
    
    from glass.sql.c import sqlcon
    
    con = sqlcon(db)
    
    cursor = con.cursor()
    
    cursor.execute(
        "UPDATE {t} SET {nullF}=COALESCE({repF}) WHERE {nullF} IS NULL".format(
            t=pgtable, nullF=nullFld, repF=replaceFld
        )
    )
    
    con.commit()
    cursor.close()
    con.close()


def distinct_to_table(db, pgtable, outable, cols=None):
    """
    Distinct values of one column to a new table
    """
    
    from glass.pys   import obj_to_lst
    from glass.sql.c import sqlcon
    
    cols = obj_to_lst(cols)
    
    if not cols:
        from glass.prop.sql import cols_name
        
        cols = cols_name(db, pgtable, api='psql')
    
    con = sqlcon(db)
    
    cs = con.cursor()
    
    cs.execute((
        "CREATE TABLE {nt} AS "
        "SELECT {cls} FROM {t} GROUP BY {cls}"
    ).format(nt=outable, cls=', '.join(cols), t=pgtable
    ))
    
    con.commit()
    cs.close()
    con.close()
    
    return outable


"""
Merge Tables
"""

def tbls_to_tbl(db, lst_tables, outTable):
    """
    Append all tables in lst_tables into the outTable
    """

    from glass.sql.q import q_to_ntbl
    
    sql = " UNION ALL ".join([
        f"SELECT * FROM {t}" for t in lst_tables])
    
    outTable = q_to_ntbl(db, outTable, sql, api='psql')
    
    return outTable
