"""
Generalization tools using SpatiaLite or PostGIS
"""

from glass.prop.sql import cols_name
from glass.pys import obj_to_lst


def st_dissolve(db, table, geomcol, outTable, whrClause=None,
                diss_cols=None, outTblIsFile=None,
                valascol=None, olyr=None,
                geomout=None, api='sqlite', multipart=True):
    """
    Dissolve a Polygon table

    API options:

    * sqlite
    * psql
    """
    
    diss_cols = obj_to_lst(diss_cols) if diss_cols else None
    sel_cols = "" if not diss_cols else f' {", ".join(diss_cols)},'

    if valascol:
        excols = ", ".join({f"{valascol[k]} AS {k}" for k in valascol})
        excols = f", {excols}," if sel_cols else f" {excols},"
    else:
        excols = ""

    gout = geomcol if not geomout else geomout
    whr = "" if not whrClause else f" WHERE {whrClause}"

    gby = "" if not diss_cols else f" GROUP BY {', '.join(diss_cols)}"

    dumps = "(ST_Dump(" if not multipart else ""
    dumpe = ")).geom" if not multipart else ""
    
    sql = (
        f"SELECT ROW_NUMBER() OVER(ORDER BY (SELECT NULL)) AS tfid,{sel_cols}{excols} "
        f"{dumps}ST_UnaryUnion(ST_Collect({geomcol})){dumpe} AS {gout} "
        f"FROM {table}{whr}{gby}"
    )
    
    if outTblIsFile:
        if api == 'sqlite':
            from glass.dtt.filter import sel_by_attr
            
            sel_by_attr(db, sql, outTable, api_gis='ogr')
        
        elif api == 'psql':
            from glass.it.shp import dbtbl_to_shp
            
            dbtbl_to_shp(
                db, sql, gout, outTable,
                api='ogr2ogr', tableIsQuery=True,
                olyr=olyr
            )
    
    else:
        from glass.sql.q import q_to_ntbl
        
        q_to_ntbl(
            db, outTable, sql,
            api='ogr2ogr' if api == 'sqlite' else 'psql'
        )
    
    return outTable



def st_diss_adjacentpoly(db, tbl, pk, geom, otbl=None, areathreshold=1000,
                         dissrule='length', cols=None, multipart=True):
    """
    Dissolve adjacent polygons

    Polygons above the thereshold not touching with other polygons
    are removed
    """

    from glass.sql.q import q_to_ntbl, exec_write_q

    _cols = obj_to_lst(cols) if cols else cols_name(db, tbl, api='psql')

    jcols = ", ".join([c for c in _cols if c != pk and c != geom])

    tcols = ", ".join([f"j.{c}" for c in _cols if c != pk and c != geom])

    foo = ", ".join([f"foo.{c}" for c in _cols if c != pk and c != geom])

    foo2 = ", ".join([f"foo2.{c}" for c in _cols if c != pk and c != geom])

    whr_rule = "foo.lenval = foo.lenmax" if dissrule == 'length' else \
        "foo.toucharea = foo.tareamax"

    mpoly = (
        f"SELECT {pk}, {jcols}, {geom} "
        f"FROM {tbl} "
        f"WHERE ST_Area({geom}) > {str(areathreshold)}"
    )

    touchq = (
        f"SELECT t.{pk} AS oldpk, j.{pk}, {tcols}, "
        f"ST_Length(ST_Intersection(t.{geom}, j.{geom})) AS lenval, "
        f"MAX(ST_Length(ST_Intersection(t.{geom}, j.{geom}))) "
            f"OVER(PARTITION BY t.{pk} ORDER BY t.{pk}) AS lenmax, "
        f"ST_Area(j.{geom}) AS toucharea, "
        f"MAX(ST_Area(j.{geom})) "
            f"OVER(PARTITION BY t.{pk} ORDER BY t.{pk}) AS tareamax, "
        f"t.{geom} "
        "FROM ("
            f"SELECT {pk}, {geom} FROM {tbl} "
            f"WHERE ST_Area({geom}) < {str(areathreshold)}"
        ") AS t "
        f"LEFT JOIN ({mpoly}) AS j "
        f"ON ST_Touches(t.{geom}, j.{geom}) "
        f"WHERE ST_Length(ST_Intersection(t.{geom}, j.{geom})) IS NOT NULL"
    )

    mq = (
        f"SELECT {pk}, {foo2}, "
        f"ST_UnaryUnion(ST_Collect(foo2.{geom})) AS {geom} "
        f"FROM ("
            f"{mpoly} "
            "UNION ALL "
            f"SELECT foo.{pk}, {foo}, foo.{geom} "
            f"FROM ({touchq}) AS foo "
            f"WHERE {whr_rule}"
        ") AS foo2 "
        f"GROUP BY {pk}, {foo2}"
    )

    if not multipart:
        _mq = (
            f"SELECT ROW_NUMBER() OVER(ORDER BY {pk}) AS {pk}, "
            f"(ST_Dump({geom})).geom AS {geom} "
            f"FROM ({mq}) AS foo3"
        )
    
    else:
        _mq = mq

    if otbl:
        ntbl = q_to_ntbl(db, otbl, _mq, api='psql')

        exec_write_q(db, [(
            f"ALTER TABLE {ntbl} ADD CONSTRAINT "
            f"{ntbl}_pk PRIMARY KEY ({pk})"
        ), (
            f"CREATE INDEX {ntbl}_geom_idx ON "
            f"{ntbl} USING gist ({geom})"
        )], api='psql')

        return otbl

    return mq

