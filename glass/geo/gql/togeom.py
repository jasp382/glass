"""
Something to Geometry
"""

def xycols_to_geom(db, intbl, x_col, y_col, outtable,
                   geom_field='geom', epsg=4326):
    """
    X and Y Colums to PostGIS Geom Column
    """
    
    from glass.sql.q import q_to_ntbl
    
    return q_to_ntbl(db, outtable, (
        "SELECT *, ST_SetSRID(ST_MakePoint({}, {}), {}) AS {} "
        "FROM {}"
    ).format(
        x_col, y_col, str(epsg), geom_field, intbl
    ), api='psql')


def geom_to_points(db, table, geomCol, outTable,
                   selCols=None, newGeomCol=None):
    """
    Convert a Polygon/Polyline Geometry to Points
    
    Equivalent to feature to point tool
    """
    
    from glass.pys   import obj_to_lst
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
    
    geomRef = geomCol if geomCol else "ST_MakePoint({}, {})".format(xCol, yCol)
    
    Q = (
        "SELECT {entCol}, ST_SetSRID(ST_MakeLine("
            "array_agg({pntCol} ORDER BY {orderF})), {srs}) "
        "FROM {tbl} GROUP BY {entCol}"
    ).format(
        entCol=entityCol, pntCol=geomRef, orderF=orderCol,
        srs=epsg, tbl=inTable
    )
    
    return q_to_ntbl(db, outTable, Q, api='psql')

