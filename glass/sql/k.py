"""
Tools to manage Table Keys
"""


from glass.sql.c import sqlcon

def create_pk(db, tbl, new_col):
    """
    Creates a new primary key field on a existent table
    """
    conn = sqlcon(db)
    
    cs = conn.cursor()
    cs.execute((
        f"ALTER TABLE {tbl} ADD COLUMN {new_col} "
        "BIGSERIAL PRIMARY KEY;"
    ))

    conn.commit()
    cs.close()
    conn.close()


def multiCols_FK_to_singleCol(db, tbl_wPk, pkCol, tbl_multiFk,
                              fkCols, newTable,
                              colsSel=None, whrCls=None):
    """
    For two tables as:
    
    Main table:
    PK | col_1 | col_2 | col_n
    1  |   0   |   0   |   0
    2  |   1   |   1   |   1
    3  |   0   |   2   |   2
    4  |   1   |   2   |   3
    
    Table with a foreign key with several columns:
    col_1 | col_2 | col_n
      0   |   0   |   0
      0   |   0   |   0
      0   |   2   |   2
      1   |   1   |   1
      1   |   2   |   3
      1   |   1   |   1
    
    Create a new table with a foreign key in a single column:
    col_1 | col_2 | col_n | FK
      0   |   0   |   0   | 1
      0   |   0   |   0   | 1
      0   |   2   |   2   | 3
      1   |   1   |   1   | 2
      1   |   2   |   3   | 4
      1   |   1   |   1   | 2
    
    In this example:
    pk_field = PK
    cols_foreign = {col_1 : col_1, col_2: col_2, col_n : col_n}
    (Keys are cols of tbl_wPk and values are cols of the tbl_multiFk
    """
    
    if type(fkCols) != dict:
        raise ValueError(
            "fkCols parameter should be a dict"
        )
    
    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_ntbl
    
    colsSel = obj_to_lst(colsSel)
    
    q = (
        "SELECT {tpk}.{pk}, {cls} FROM {tfk} "
        "INNER JOIN {tpk} ON {tblRel}{whr}"
    ).format(
        tpk=tbl_wPk, pk=pkCol, tfk=tbl_multiFk,
        cls="{}.*".format(tbl_multiFk) if not colsSel else \
            ", ".join(["{}.{}".format(tbl_wPk, pkCol) for c in colsSel]),
        tblRel=" AND ".join([
            "{}.{} = {}.{}".format(
                tbl_multiFk, fkCols[k], tbl_wPk, k
            ) for k in fkCols
        ]),
        whr="" if not whrCls else f" WHERE {whrCls}"
    )
    
    outbl = q_to_ntbl(db, newTable, q, api='psql')
    
    return outbl

