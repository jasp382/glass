"""
Tools for process geographic data on PostGIS
"""


def st_buffer(db, inTbl, bfDist, geomCol, output=None, bufferField="geometry",
              whrClause=None, dissolve=None, cols_select=None, outTblIsFile=None,
              olyr=None):
    """
    Using Buffer on PostGIS Data
    """
    
    from glass.pys import obj_to_lst
    
    dissolve = dissolve if dissolve == "ALL" or dissolve == 'SEL' else None

    dissolve = "ALL" if dissolve == 'SEL' and not cols_select else dissolve
    
    selcols = " " if not cols_select or dissolve == 'ALL' else \
        f" {', '.join(obj_to_lst(cols_select))}, "
    
    bf_start = "ST_Buffer(" if not dissolve else \
        "ST_UnaryUnion(ST_Collect(ST_Buffer("
    
    bf_end = ")" if not dissolve else ")))"

    whr = "" if not whrClause else f" WHERE {whrClause}"

    gby = selcols[1:-2] if cols_select and dissolve == 'SEL' else ""
    
    gby = gby if not gby else f" GROUP BY {gby}"
    
    Q = (
        f"SELECT{selcols}{bf_start}{geomCol}, {bfDist}"
        f"{bf_end} AS {bufferField} "
        f"FROM {inTbl} AS bft{whr}{gby}"
    )
    
    if output and not outTblIsFile:
        from glass.sql.q import q_to_ntbl
        
        outTbl = q_to_ntbl(db, output, Q, api='psql')

        return outTbl
    
    elif output and outTblIsFile:
        from glass.it.shp import dbtbl_to_shp
        
        dbtbl_to_shp(
            db, Q, bufferField, output, api='ogr2ogr',
            tableIsQuery=True, olyr=olyr
        )

        return output
    
    else:
        return Q


def splite_buffer(db, table, dist, geomField, outTbl,
              cols_select=None, bufferField="geometry",
              whrClause=None, outTblIsFile=None, dissolve=None):
    """
    Run ST_Buffer
    
    if not dissolve, no generalization will be applied; 
    if dissolve == to str or list, a generalization will be accomplish
    using the fields referenced by this object;
    if dissolve == 'ALL', all features will be dissolved.
    """
    
    from glass.pys import obj_to_lst
    
    dissolve = obj_to_lst(dissolve) if dissolve != "ALL" else "ALL"

    sel = " " if not cols_select else f" {', '.join(obj_to_lst(cols_select))}, "

    bfstart = "ST_Buffer(" if not dissolve else "ST_UnaryUnion(ST_Collect(ST_Buffer("
    bfend   = ")" if not dissolve else ")))"

    whr="" if not whrClause else f" WHERE {whrClause}"

    gby = "" if not dissolve or dissolve == "ALL" else f" GROUP BY {', '.join(dissolve)}"
    
    sql = (
        f"SELECT{sel}{bfstart}{geomField}, "
        f"{str(dist)}{bfend} AS {bufferField} "
        f"FROM {table}{whr}{gby}"
    )
    
    if outTblIsFile:
        from glass.dtt.filter import sel_by_attr
        
        sel_by_attr(db, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.sql.q import q_to_ntbl
        
        q_to_ntbl(db, outTbl, sql, api='ogr2ogr')
    
    return outTbl

