"""
Projections in SQL
"""

def sql_proj(dbname, tbl, otbl, oepsg, cols=None, geomCol=None,
    newGeom=None, whr=None, new_pk=None):
    """
    Reproject geometric layer to another spatial reference system (srs)
    """

    from glass.pyt    import obj_to_lst
    from glass.sql.to import q_to_ntbl

    geomCol = 'geom' if not geomCol else geomCol
    newGeom = 'geom' if not newGeom else newGeom

    if not cols:
        from glass.sql.i import cols_name

        cols = cols_name(dbname, tbl)

        cols.remove(geomCol)
    
    else:
        cols = obj_to_lst(cols)

        if geomCol in cols and geomCol == newGeom:
            cols.remove(geomCol)
            cols.append('{c} AS old_{c}'.format(c=geomCol))

    Q = (
        "SELECT {}, ST_Transform({}, {}) AS {} "
        "FROM {}{}"
    ).format(
        ", ".join(cols), geomCol, str(oepsg), newGeom, tbl,
        "" if not whr else " WHERE {}".format(whr)
    )

    otbl = q_to_ntbl(dbname, otbl, Q, api='psql')

    if new_pk:
        from glass.sql.k  import create_pk

        create_pk(dbname, otbl, new_pk)

    return otbl

