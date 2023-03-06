"""
Geometric Conversion using SQL
"""

def lnh_to_polg(db, intbl, outtbl):
    """
    Line to Polygons
    """
    
    from glass.sql.q import q_to_ntbl
    
    Q = (
        "SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS gid, "
        "(ST_Dump(ST_Polygonize(geom))).geom AS geom FROM ("
            "SELECT ST_Node(ST_Collect(geom)) AS geom FROM ("
                f"SELECT (ST_Dump(geom)).geom FROM {intbl}"
            ") AS foo"
        ") AS foo"
    )
    
    return q_to_ntbl(db, outtbl, Q)


def geom_to_points(db, table, geomCol, outTable,
                   selCols=None, newGeomCol=None):
    """
    Convert a Polygon/Polyline Geometry to Points
    
    Equivalent to feature to point tool
    """
    
    from glass.pys   import obj_to_lst
    from glass.sql.q import q_to_ntbl
    
    selCols = obj_to_lst(selCols)

    cols = "" if not selCols else f"{', '.join(selCols)}, "

    newCol="geom" if not newGeomCol else newGeomCol
    
    Q = (
        f"SELECT {cols}(ST_DumpPoints("
            f"{geomCol})).geom AS {newCol} "
        f"FROM {table}"
    )
    
    return q_to_ntbl(db, outTable, Q, api='psql')


def pnts_to_lines(db, inTable, outTable, entityCol, orderCol,
                  geomCol=None, xCol=None, yCol=None, epsg=4326):
    """
    Given a table with points by entity, create a new table with a polyline
    for each entity. The points are added to the polyline based on a 
    sequence in one column.
    """
    
    if not geomCol:
        if not xCol or not yCol:
            raise ValueError(
                'If geomCol is not specified, xCol and ycol must replace it!')
    
    from glass.sql.q import q_to_ntbl
    
    geomRef = geomCol if geomCol else f"ST_MakePoint({xCol}, {yCol})"
    
    Q = (
        f"SELECT {entityCol}, ST_SetSRID(ST_MakeLine("
            f"array_agg({geomRef} ORDER BY {orderCol})), {epsg}) "
        f"FROM {inTable} GROUP BY {entityCol}"
    )
    
    return q_to_ntbl(db, outTable, Q, api='psql')


def add_endpnt_to_tbl(db, inTable, outTable, 
                           idCol='gid', geomCol='geom',
                           startCol="start_vertex",
                           endCol="end_vertex"):
    """
    Add start/end points columns to table
    """
    
    from glass.sql.q    import q_to_ntbl
    from glass.prop.sql import cols_name
    
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

