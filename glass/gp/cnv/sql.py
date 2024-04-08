"""
Geometric Conversion using PostGIS
"""

from glass.prop.sql import cols_name
from glass.pys      import obj_to_lst
from glass.it.shp   import dbtbl_to_shp
from glass.sql.q    import q_to_ntbl


def feat_to_polg(db: str, intbl: str, geomcol: str, out: str|None=None,
                 out_is_file:bool|None=None, ogeom:str|None="geom", outpk:str|None="gid",
                 olyr:str|None=None) -> str:
    """
    Feature to Polygons
    """

    ogeom = geomcol if not ogeom else ogeom
    opk   = "gid" if not outpk else outpk
    
    q = (
        f"SELECT ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS {opk}, "
        f"(ST_Dump(ST_Polygonize({ogeom}))).geom AS {ogeom} FROM ("
            f"SELECT ST_Node(ST_Collect({ogeom})) AS {ogeom} FROM ("
                f"SELECT (ST_Dump({geomcol})).geom AS {ogeom} "
                f"FROM ({intbl}) AS foo1"
            ") AS foo"
        ") AS foo2"
    )

    if out and out_is_file:
        dbtbl_to_shp(
            db, q, ogeom, out,
            api="ogr2ogr", tableIsQuery=True,
            olyr=olyr
        )

        return out
    
    elif out and not out_is_file:
        return q_to_ntbl(db, out, q, api='psql')
    
    else:
        return q


def st_feat_to_lnh(db: str, table: str, pk:str, geomcol: str, out: str|None=None,
                   out_is_file:bool|None=None, whr: str|None=None,
                   sel_cols:str|list[str]|None=None, ogeom:str|None="geom",
                   outsrs:int|None=None, olyr:str|None=None) -> str:
    """
    Feature to Lines
    """

    ogeom = geomcol if not ogeom else ogeom

    if sel_cols:
        sel_cols = obj_to_lst(sel_cols)
    else:
        sel_cols = cols_name(db, table)
    
    _sel_cols = [f"jt.{x}" for x in sel_cols if x != pk and x != geomcol]
    
    str_cols = ", ".join(_sel_cols)

    igeom = geomcol if not outsrs else f"ST_Transform({geomcol}, {str(outsrs)})"

    strwhr = "" if not whr else f" AND {whr}"

    mq = (
        f"SELECT {pk}, ST_Collect(ST_ExteriorRing({ogeom})) AS {ogeom} "
        "FROM ("
            f"SELECT {pk}, (ST_Dump({ogeom})).geom "
            "FROM ("
                f"SELECT {pk}, {igeom} AS {ogeom} "
                f"FROM {table} "
                f"WHERE ST_IsValid({geomcol}){strwhr}"
            ") AS foo"
        ") AS foo2 "
        f"GROUP BY {pk}"
    )

    fq = (
        f"SELECT mt.{pk}, mt.{ogeom}, {str_cols} "
        f"FROM ({mq}) AS mt "
        f"LEFT JOIN {table} AS jt "
        f"ON mt.{pk} = jt.{pk}"
    )

    if out and out_is_file:
        dbtbl_to_shp(
            db, fq, ogeom, out,
            api="ogr2ogr", tableIsQuery=True,
            olyr=olyr
        )

        return out
    
    elif out and not out_is_file:
        q_to_ntbl(db, out, fq, api='psql')

        return out
    
    else:
        return fq


def st_lnh_to_poly(db:str, tbl:str, geomc:str, out: str|None=None,
                   out_is_file:bool|None=None,
                   sel_cols:str|list[str]|None=None,
                   ogeom:str|None='geom',
                   olyr:str|None=None):
    """
    Lines to polygons
    """

    ogeom = "geom" if not ogeom else ogeom

    if sel_cols:
        sel_cols = obj_to_lst(sel_cols)
    else:
        sel_cols = cols_name(db, tbl)
    
    _sel_cols = [x for x in sel_cols if x != geomc]
    
    str_cols1 = ", ".join([f"foo.{c}" for c in _sel_cols])
    str_cols2 = ", ".join([f"itbl.{c}" for c in _sel_cols])

    q = (
        f"SELECT {str_cols1}, ST_MakePolygon({ogeom}) AS {ogeom} "
        "FROM ("
            f"SELECT {str_cols2}, (ST_Dump({geomc})).geom AS {ogeom} "
            f"FROM ({tbl}) AS itbl"
        ") AS foo"
    )

    if out and out_is_file:
        dbtbl_to_shp(
            db, q, ogeom, out,
            api="ogr2ogr", tableIsQuery=True,
            olyr=olyr
        )

        return out

    elif out and not out_is_file:
        q_to_ntbl(db, out, q, api='psql')

        return out
    
    else:
        return q


def geom_to_points(db, table, geomCol, outTable,
                   selCols=None, newGeomCol=None):
    """
    Convert a Polygon/Polyline Geometry to Points
    
    Equivalent to feature to point tool
    """
    
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


def polyg_to_lines(db, itbl, geomcol, otbl, 
                   out_is_file=None, olyr=None, outsrs=None):
    """
    Polygons to Lines
    """

    gg = f"ST_Transform({geomcol}, {str(outsrs)})" \
        if outsrs else geomcol

    sql = (
        "SELECT (ST_Dump(ST_LineMerge(ST_Collect("
            f"ST_Boundary({gg}))))).geom AS {geomcol}, "
        "ROW_NUMBER() OVER() AS cat "
        f"FROM {itbl} AS mtbl"
    )

    if out_is_file:
        dbtbl_to_shp(
            db, sql, geomcol, otbl,
            api='ogr2ogr', tableIsQuery=True,
            olyr=olyr
        )
    
    else:
        q_to_ntbl(
            db, otbl, sql,
            api="ogr2ogr"
        )
    
    return otbl

