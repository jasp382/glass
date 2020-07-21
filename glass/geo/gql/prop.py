"""
Geometric Properties
"""

def tbl_ext(db, table, geomCol):
    """
    Return extent of the geometries in one pgtable
    """
    
    from glass.dct.fm.sql import q_to_obj
    
    q = (
        "SELECT MIN(ST_X(pnt_geom)) AS eleft, MAX(ST_X(pnt_geom)) AS eright, "
        "MIN(ST_Y(pnt_geom)) AS bottom, MAX(ST_Y(pnt_geom)) AS top "
        "FROM ("
            "SELECT (ST_DumpPoints({geomcol})).geom AS pnt_geom "
            "FROM {tbl}"
        ") AS foo"
    ).format(tbl=table, geomcol=geomCol)
    
    ext = q_to_obj(db, q, db_api='psql').to_dict(orient='index')[0]
    
    return [
        ext['eleft'], ext['bottom'], ext['eright'], ext['top']
    ]


def tbl_geomtype(db, table, geomCol='geom'):
    """
    Return the number of geometry types in table
    """
    
    from glass.dct.fm.sql import q_to_obj
    
    return int(q_to_obj(db, (
        "SELECT COUNT(*) AS row_count FROM ("
            "SELECT ST_GeometryType((ST_Dump({})).geom) AS cnt_geom "
            "FROM {} GROUP BY ST_GeometryType((ST_Dump({})).geom)"
        ") AS foo"
    ).format(geomCol, table, geomCol), db_api='psql').iloc[0].row_count)


def select_main_geom_type(db, table, outbl, geomCol='geom'):
    """
    Assuming a table with several geometry types, this method
    counts the rows for each geometry type and select the rows with a geometry
    type with more rows
    """
    
    from glass.dct.to.sql import q_to_ntbl
    from glass.sql.i  import cols_name
    
    COLS = [x for x in cols_name(
        db, table, sanitizeSpecialWords=None
    ) if x != geomCol]
    
    Q = (
        "SELECT {cols}, {geomcol} FROM ("
            "SELECT *, MAX(jtbl.geom_cont) OVER (PARTITION BY "
            "jtbl.tst) AS max_cnt FROM ("
                "SELECT {cols}, (ST_Dump({geomcol})).geom AS {geomcol}, "
                "ST_GeometryType((ST_Dump({geomcol})).geom) AS geom_type "
                "FROM {tbl}"
            ") AS foo INNER JOIN ("
                "SELECT ST_GeometryType((ST_Dump({geomcol})).geom) AS gt, "
                "COUNT(ST_GeometryType((ST_Dump({geomcol})).geom)) AS geom_cont, "
                "1 AS tst FROM {tbl} GROUP BY ST_GeometryType((ST_Dump({geomcol})).geom)"
            ") AS jtbl ON foo.geom_type = jtbl.gt"
        ") AS foo WHERE geom_cont = max_cnt"
    ).format(
        cols=", ".join(COLS), geomcol=geomCol,
        tbl=table
    )
    
    return q_to_ntbl(db, outbl, Q, api='psql')


def check_endpoint_ispoint(db, lnhTable, pntTable, outTable,
                           nodeStart, nodeEnd, pointId, pntGeom="geom"):
    """
    Check if a Start/End point in a table with line geometries is a point 
    in other table.
    """
    
    from glass.dct.to.sql import q_to_ntbl
    from glass.sql.i  import cols_name
    
    tCols = [x for x in cols_name(
        db, lnhTable) if x != nodeStart and x != nodeEnd
    ]
    
    return q_to_ntbl(db, outTable, (
        "SELECT * FROM ("
            "SELECT {fooCols}, foo.{stPnt}, foo.{endPnt}, "
            "CASE "
                "WHEN start_tbl.start_x IS NOT NULL THEN 1 ELSE 0 "
            "END AS start_isstop, "
            "CASE "
                "WHEN end_tbl.end_x IS NOT NULL THEN 1 ELSE 0 "
            "END AS end_isstop, start_tbl.start_id, end_tbl.end_id "
            "FROM ("
                "SELECT *, "
                "CAST(((round(CAST(ST_X({stPnt}) AS numeric), 4)) * 10000) "
                    "AS integer) AS start_x, "
                "CAST(((round(CAST(ST_Y({stPnt}) AS numeric), 4)) * 10000) "
                    "AS integer) AS start_y, "
                "CAST(((round(CAST(ST_X({endPnt}) AS numeric), 4)) * 10000) "
                    "AS integer) AS end_x, "
                "CAST(((round(CAST(ST_Y({endPnt}) AS numeric), 4)) * 10000) "
                    "AS integer) AS end_y "
                "FROM {lnhT}"
            ") AS foo "
            "LEFT JOIN ("
                "SELECT CAST(((round(CAST(ST_X({pntG}) AS numeric), 4)) "
                    "* 10000) AS integer) AS start_x, "
                "CAST(((round(CAST(ST_Y({pntG}) AS numeric), 4)) "
                    "* 10000) AS integer) AS start_y, "
                "{pntid} AS start_id FROM {pntT}"
            ") AS start_tbl "
            "ON foo.start_x = start_tbl.start_x AND "
            "foo.start_y = start_tbl.start_y "
            "LEFT JOIN ("
                "SELECT CAST(((round(CAST(ST_X({pntG}) AS numeric), 4)) "
                    "* 10000) AS integer) AS end_x, "
                "CAST(((round(CAST(ST_Y({pntG}) AS numeric), 4)) "
                    "* 10000) as integer) AS end_y, "
                "{pntid} AS end_id FROM {pntT}"
            ") AS end_tbl "
            "ON foo.end_x = end_tbl.end_x AND foo.end_y = end_tbl.end_y"
        ") AS foo2 "
        "GROUP BY {cols}, {stPnt}, {endPnt}, start_isstop, end_isstop, "
        "start_id, end_id"
    ).format(
        fooCols = ", ".join(["foo.{}".format(c) for c in tCols]),
        stPnt = nodeStart, endPnt = nodeEnd, lnhT = lnhTable,
        pntT = pntTable, pntG = pntGeom,
        cols = ", ".join(tCols), pntid=pointId
    ), api='psql')

