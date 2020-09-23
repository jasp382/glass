"""
Manage fields
"""

from glass.sql.c import sqlcon
from glass.sql.q import q_to_ntbl


"""
Operations
"""
def add_field(db, pgtable, columns):
    """
    Add new field to a table
    """
    
    # Verify is columns is a dict
    if type(columns) != dict:
        raise ValueError(
            'columns should be a dict (name as keys; field type as values)'
        )
    
    con = sqlcon(db)
    
    cursor = con.cursor()
    
    cursor.execute("ALTER TABLE {} ADD {};".format(
        pgtable,
        ", ".join(["{} {}".format(x, columns[x]) for x in columns])
    ))
    
    con.commit()
    cursor.close()
    con.close()


def drop_col(db, pg_table, columns):
    """
    Delete column from pg_table
    """
    
    from glass.pys  import obj_to_lst
    
    con = sqlcon(db)
    
    cursor = con.cursor()
    
    columns = obj_to_lst(columns)
    
    cursor.execute('ALTER TABLE {} {};'.format(
        pg_table, ', '.join(['DROP COLUMN {}'.format(x) for x in columns])
    ))
    
    con.commit()
    cursor.close()
    con.close()


def change_field_type(db, table, fields, outable, cols=None):
    """
    Imagine a table with numeric data saved as text. This method convert
    that numeric data to a numeric field.
    
    fields = {'field_name' : 'field_type'}
    """

    from glass.sql.prop import cols_name
    
    if not cols:
        cols = cols_name(db, table)
    
    else:
        from glass.pys  import obj_to_lst
        
        cols = obj_to_lst(cols)
    
    select_fields = [f for f in cols if f not in fields]
    
    con = sqlcon(db)
    
    # Create new table with the new field with converted values
    cursor = con.cursor()
    
    cursor.execute((
        'CREATE TABLE {} AS SELECT {}, {} FROM {}'
    ).format(
        outable,
        ', '.join(select_fields),
        ', '.join(['CAST({f_} AS {t}) AS {f_}'.format(
            f_=f, t=fields[f]) for f in fields
        ]),
        table
    ))
    
    con.commit()
    cursor.close()
    con.close()


def split_colval_into_cols(db_name, table, column, splitChar,
                                    new_cols, new_table):
    """
    Split column value into several columns
    """

    from glass.sql.prop import cols_name
    
    if type(new_cols) != list:
        raise ValueError(
            'new_cols should be a list'
        )
    
    nr_cols = len(new_cols)
    
    if nr_cols < 2:
        raise ValueError(
            'new_cols should have 2 or more elements'
        )
    
    # Get columns types from table
    tblCols = cols_name(db_name, table)
    
    # SQL construction
    SQL = "SELECT {}, {} FROM {}".format(
        ", ".join(tblCols),
        ", ".join([
            "split_part({}, '{}', {}) AS {}".format(
                column, splitChar, i+1, new_cols[i]
            ) for i in range(len(new_cols))
        ]),
        table
    )
    
    q_to_ntbl(db_name, new_table, SQL, api='psql')
    
    return new_table


def txt_cols_to_col(db, inTable, columns, strSep, newCol, outTable=None):
    """
    Several text columns to a single column
    """
    
    from glass.pys   import obj_to_lst
    from glass.sql.prop import cols_type
    
    mergeCols = obj_to_lst(columns)
    
    tblCols = cols_type(db, inTable, sanitizeColName=None, pyType=False)
    
    for col in mergeCols:
        if tblCols[col] != 'text' and tblCols[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    coalesce = ""
    for i in range(len(mergeCols)):
        if not i:
            coalesce += "COALESCE({}, '')".format(mergeCols[i])
        
        else:
            coalesce += " || '{}' || COALESCE({}, '')".format(
                strSep, mergeCols[i])
    
    
    if outTable:
        # Write new table
        colsToSelect = [_c for _c in tblCols if _c not in mergeCols]
        
        if not colsToSelect:
            sel = coalesce + " AS {}".format(newCol)
        else:
            sel = "{}, {}".format(
                ", ".join(colsToSelect), coalesce + " AS {}".format(newCol)
            )
        
        q_to_ntbl(db, outTable, "SELECT {} FROM {}".format(
            sel, inTable), api='psql')
        
        return outTable
    
    else:
        # Add column to inTable
        from glass.sql.tbl import update_table
        
        add_field(db, inTable, {newCol : 'text'})
        
        update_table(db, inTable, {newCol : coalesce})
        
        return inTable


def col_to_timestamp(db, inTbl, dayCol, hourCol, minCol, secCol, newTimeCol,
                     outTbl, selColumns=None, whr=None):
    
    """
    Columns to timestamp column
    """
    
    from glass.pys import obj_to_lst
    
    selCols = obj_to_lst(selColumns)
    
    sql = (
        "SELECT {C}, TO_TIMESTAMP("
            "COALESCE(CAST({day} AS text), '') || ' ' || "
            "COALESCE(CAST({hor} AS text), '') || ':' || "
            "COALESCE(CAST({min} AS text), '') || ':' || "
            "COALESCE(CAST({sec} AS text), ''), 'YYYY-MM-DD HH24:MI:SS'"
        ") AS {TC} FROM {T}{W}"
    ).format(
        C   = "*" if not selCols else ", ".join(selCols),
        day = dayCol, hor=hourCol, min=minCol, sec=secCol,
        TC  = newTimeCol, T=inTbl,
        W   = "" if not whr else " WHERE {}".format(whr)
    )
    
    q_to_ntbl(db, outTbl, sql, api='psql')
    
    return outTbl


def trim_char_in_col(db, pgtable, cols, trim_str, outTable,
                     onlyTrailing=None, onlyLeading=None):
    """
    Python implementation of the TRIM PSQL Function
    
    The PostgreSQL trim function is used to remove spaces or set of
    characters from the leading or trailing or both side from a string.
    """
    
    from glass.pys   import obj_to_lst
    from glass.sql.prop import cols_type
    
    cols = obj_to_lst(cols)
    
    colsTypes = cols_type(db, pgtable,
        sanitizeColName=None, pyType=False)
    
    for col in cols:
        if colsTypes[col] != 'text' and colsTypes[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    colsToSelect = [_c for _c in colsTypes if _c not in cols]
    
    tail_lead_str = "" if not onlyTrailing and not onlyLeading else \
        "TRAILING " if onlyTrailing and not onlyLeading else \
        "LEADING " if not onlyTrailing and onlyLeading else ""
    
    trimCols = [
        "TRIM({tol}{char} FROM {c}) AS {c}".format(
            c=col, tol=tail_lead_str, char=trim_str
        ) for col in cols
    ]
    
    if not colsToSelect:
        cols_to_select = "{}".format(", ".join(trimCols))
    else:
        cols_to_select = "{}, {}".format(
            ", ".join(colsToSelect), ", ".join(trimCols)
        )
    
    q_to_ntbl(db, outTable,
        "SELECT {} FROM {}".format(colsToSelect, pgtable), api='psql'
    )


def replace_char_in_col(db, pgtable, cols, match_str, replace_str, outTable):
    """
    Replace char in all columns in cols for the value of replace_str
    
    Python implementation of the REPLACE PSQL Function
    """
    
    from glass.pys   import obj_to_lst
    from glass.sql.prop import cols_type
    
    cols = obj_to_lst(cols)
    
    colsTypes = cols_type(db, pgtable,
        sanitizeColName=None, pyType=False)
    
    for col in cols:
        if colsTypes[col] != 'text' and colsTypes[col] != 'varchar':
            raise ValueError('{} should be of type text'.format(col))
    
    colsToSelect = [_c for _c in colsTypes if _c not in cols]
    
    colsReplace  = [
        "REPLACE({c}, '{char}', '{nchar}') AS {c}".format(
            c=col, char=match_str, nchar=replace_str
        ) for col in cols
    ]
    
    if not colsToSelect:
        cols_to_select = "{}".format(", ".join(colsReplace))
    else:
        cols_to_select = "{}, {}".format(
            ", ".join(colsToSelect), ", ".join(colsReplace))
    
    q_to_ntbl(db, outTable, "SELECT {cols} FROM {tbl}".format(
        cols  = cols_to_select, tbl   = pgtable
    ), api='psql')
    
    return outTable


def substr_to_newcol(db, table, field, newCol,
    idxFrom, idxTo):
    """
    Get substring of string by range
    """
    
    from glass.sql.q import exec_write_q
    
    # Add new field to table
    add_field(db, table, {newCol : "text"})
    
    # Update table
    exec_write_q(db, (
        "UPDATE {tbl} SET {nf} = substring({f} from {frm} for {to}) "
        "WHERE {nf} IS NULL"
    ).format(
        tbl=table, nf=newCol, f=field, frm=idxFrom,
        to=idxTo
    ), api='psql')
    
    return table


def add_geomtype_to_col(db, table, newCol, geomCol):
    """
    Add Geom Type to Column
    """
    
    from glass.sql.q import exec_write_q
    
    # Add new field to table
    add_field(db, table, {newCol : "text"})
    
    exec_write_q(db, "UPDATE {} SET {} = ST_GeometryType({})".format(
        table, newCol, geomCol
    ), api='psql')
    
    return table

