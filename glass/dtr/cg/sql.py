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
                "SELECT (ST_Dump(geom)).geom FROM {}"
            ") AS foo"
        ") AS foo"
    ).format(intbl)
    
    return q_to_ntbl(db, outtbl, Q)


def geom_to_points(db, table, geomCol, outTable,
                   selCols=None, newGeomCol=None):
    """
    Convert a Polygon/Polyline Geometry to Points
    
    Equivalent to feature to point tool
    """
    
    from glass.pys      import obj_to_lst
    from glass.sql.q import q_to_ntbl
    
    selCols = obj_to_lst(selCols)
    
    Q = (
        "SELECT {cols}(ST_DumpPoints({geom})).geom AS {newCol} "
        "FROM {tbl}"
    ).format(
        cols = "" if not selCols else "{}, ".format(", ".join(selCols)),
        geom=geomCol, newCol="geom" if not newGeomCol else newGeomCol,
        tbl=table
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

    cols = ", ".join(cols_name(db, inTable))
    
    return q_to_ntbl(db, outTable, (
        f"SELECT {cols}, {startCol}, {endCol} FROM ("
            f"SELECT *, lead({startCol}) OVER ("
                f"PARTITION BY {idCol} ORDER BY pnt_idx) AS {endCol} "
            "FROM ("
                f"SELECT {cols}, pnt_idx, {startCol}, "
                "CASE "
                    "WHEN pnt_idx = 1 OR pnt_idx = MAX(pnt_idx) "
                        f"OVER (PARTITION BY {idCol}) "
                    "THEN 1 ELSE 0 END AS pnt_cat "
                "FROM ("
                    "SELECT {cols}, "
                    f"(ST_DumpPoints({geomCol})).path[1] AS pnt_idx, "
                    f"(ST_DumpPoints({geomCol})).geom AS {startCol} "
                    "FROM {table}"
                ") AS foo"
            ") AS foo2 "
            "WHERE pnt_cat = 1"
        ") AS foo3 "
        f"WHERE {endCol} IS NOT NULL "
        f"ORDER BY {idCol}, pnt_idx"
    ), api='psql')

