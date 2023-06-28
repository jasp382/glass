"""
Generalization tools using SpatiaLite or PostGIS
"""

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
    
    from glass.pys import obj_to_lst
    
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
        f"SELECT{sel_cols}{excols} "
        f"{dumps}ST_UnaryUnion(ST_Collect({geomcol})){dumpe} AS {gout} "
        f"FROM {table}{whr}{gby}"
    )
    
    if outTblIsFile:
        if api == 'sqlite':
            from glass.tbl.filter import sel_by_attr
            
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

