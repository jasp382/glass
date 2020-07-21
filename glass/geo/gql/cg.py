"""
Change Geometry
"""


def add_endpnt_to_tbl(db, inTable, outTable, 
                           idCol='gid', geomCol='geom',
                           startCol="start_vertex",
                           endCol="end_vertex"):
    """
    Add start/end points columns to table
    """
    
    from glass.dct.to.sql import q_to_ntbl
    from glass.sql.i  import cols_name
    
    return q_to_ntbl(db, outTable, (
        "SELECT {cols}, {stPnt}, {endPnt} FROM ("
            "SELECT *, lead({stPnt}) OVER ("
                "PARTITION BY {colId} ORDER BY pnt_idx) AS {endPnt} "
            "FROM ("
                "SELECT {cols}, pnt_idx, {stPnt}, "
                "CASE "
                    "WHEN pnt_idx = 1 OR pnt_idx = MAX(pnt_idx) "
                        "OVER (PARTITION BY {colId}) "
                    "THEN 1 ELSE 0 END AS pnt_cat "
                "FROM ("
                    "SELECT {cols}, "
                    "(ST_DumpPoints({geomF})).path[1] AS pnt_idx, "
                    "(ST_DumpPoints({geomF})).geom AS {stPnt} "
                    "FROM {table}"
                ") AS foo"
            ") AS foo2 "
            "WHERE pnt_cat = 1"
        ") AS foo3 "
        "WHERE {endPnt} IS NOT NULL "
        "ORDER BY {colId}, pnt_idx"
    ).format(
        cols  =", ".join(cols_name(db, inTable)),
        stPnt = startCol, endPnt = endCol, colId = idCol,
        geomF = geomCol , table  = inTable
    ), api='psql')

