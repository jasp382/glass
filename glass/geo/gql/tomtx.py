"""
Produce Matrices from Data
"""

def tbl_to_area_mtx(db, tbl, cola, colb, result):
    """
    Table to Matrix
    
    Table as:
        FID | col_a | col_b | geom
    0 |  1  |   A   |   A   | ....
    0 |  2  |   A   |   B   | ....
    0 |  3  |   A   |   A   | ....
    0 |  4  |   A   |   C   | ....
    0 |  5  |   A   |   B   | ....
    0 |  6  |   B   |   A   | ....
    0 |  7  |   B   |   A   | ....
    0 |  8  |   B   |   B   | ....
    0 |  9  |   B   |   B   | ....
    0 | 10  |   C   |   A   | ....
    0 | 11  |   C   |   B   | ....
    0 | 11  |   C   |   D   | ....
    
    To:
    classe | A | B | C | D
       A   |   |   |   | 
       B   |   |   |   |
       C   |   |   |   |
       D   |   |   |   |
    
    cola = rows
    colb = cols
    """

    from glass.dct.to.sql import q_to_ntbl
    from glass.dct.fm.sql import q_to_obj

    ref_val = q_to_obj(db, (
        "SELECT fcol FROM ("
            "SELECT CAST({map1_cls} AS text) AS fcol FROM {tbl} "
            "GROUP BY {map1_cls} "
            "UNION ALL "
            "SELECT CAST({map2_cls} AS text) AS fcol FROM {tbl} "
            "GROUP BY {map2_cls}"
        ") AS foo GROUP BY fcol ORDER BY fcol"
    ).format(
        tbl = tbl, map1_cls = cola, map2_cls = colb,
    ), db_api='psql').fcol.tolist()

    mtx_tbl = q_to_ntbl(db, result, (
        "SELECT * FROM crosstab('"
            "SELECT CASE "
                "WHEN foo.{map1_cls} IS NOT NULL "
                "THEN foo.{map1_cls} ELSE jtbl.flyr "
            "END AS lulc1_cls, CASE "
                "WHEN foo.{map2_cls} IS NOT NULL "
                "THEN foo.{map2_cls} ELSE jtbl.slyr "
            "END AS lulc2_cls, CASE "
                "WHEN foo.garea IS NOT NULL "
                "THEN round(CAST(foo.garea / 1000000 AS numeric)"
                ", 3) ELSE 0 "
            "END AS garea FROM ("
                "SELECT CAST({map1_cls} AS text) AS {map1_cls}, "
                "CAST({map2_cls} AS text) AS {map2_cls}, "
                "SUM(ST_Area(geom)) AS garea "
                "FROM {tbl} GROUP BY {map1_cls}, {map2_cls}"
            ") AS foo FULL JOIN ("
                "SELECT f.flyr, s.slyr FROM ("
                    "SELECT CAST({map1_cls} AS text) AS flyr "
                    "FROM {tbl} GROUP BY {map1_cls}"
                ") AS f, ("
                    "SELECT CAST({map2_cls} AS text) AS slyr "
                    "FROM {tbl} GROUP BY {map2_cls}"
                ") AS s"
            ") AS jtbl "
            "ON foo.{map1_cls} = jtbl.flyr AND "
            "foo.{map2_cls} = jtbl.slyr "
            "ORDER BY 1,2"
        "') AS ct("
            "lulc_cls text, {crossCols}"
        ")"
    ).format(
        crossCols = ", ".join([
            "cls_{} numeric".format(c) for c in ref_val
        ]), tbl = tbl,
        map1_cls = cola, map2_cls = colb
    ), api='psql')

    return mtx_tbl

