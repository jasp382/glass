"""
Tools for process geographic data on PostGIS
"""


def st_buffer(db, inTbl, bfDist, geomCol, outTbl, bufferField="geometry",
              whrClause=None, dissolve=None, cols_select=None, outTblIsFile=None):
    """
    Using Buffer on PostGIS Data
    """
    
    from glass.pys import obj_to_lst
    
    dissolve = obj_to_lst(dissolve) if dissolve != "ALL" else "ALL"
    
    SEL_COLS = "" if not cols_select else ", ".join(obj_to_lst(cols_select))
    DISS_COLS = "" if not dissolve or dissolve == "ALL" else ", ".join(dissolve)
    GRP_BY = "" if not dissolve else "{}, {}".format(SEL_COLS, DISS_COLS) if \
        SEL_COLS != "" and DISS_COLS != "" else SEL_COLS \
        if SEL_COLS != "" else DISS_COLS if DISS_COLS != "" else ""
    
    Q = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {t}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(SEL_COLS),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        geom=geomCol, _dist=bfDist,
        endFunc=")" if not dissolve else ")))",
        t=inTbl,
        grpBy=" GROUP BY {}".format(GRP_BY) if GRP_BY != "" else "",
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        bf=bufferField
    )
    
    if not outTblIsFile:
        from glass.ng.sql.q import q_to_ntbl
        
        outTbl = q_to_ntbl(db, outTbl, Q, api='psql')
    
    else:
        from glass.g.it.shp import dbtbl_to_shp
        
        dbtbl_to_shp(db, Q, bufferField, outTbl, api='pgsql2shp',
            tableIsQuery=True
        )
    
    return outTbl

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
    
    sql = (
        "SELECT{sel}{spFunc}{geom}, {_dist}{endFunc} AS {bf} "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        sel = " " if not cols_select else " {}, ".format(
            ", ".join(obj_to_lst(cols_select))
        ),
        tbl=table,
        geom=geomField, _dist=str(dist), bf=bufferField,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        spFunc="ST_Buffer(" if not dissolve else \
            "ST_UnaryUnion(ST_Collect(ST_Buffer(",
        endFunc = ")" if not dissolve else ")))",
        grpBy="" if not dissolve or dissolve == "ALL" else " GROUP BY {}".format(
            ", ".join(dissolve)
        )
    )
    
    if outTblIsFile:
        from glass.g.tbl.filter import sel_by_attr
        
        sel_by_attr(db, sql, outTbl, api_gis='ogr')
    
    else:
        from glass.ng.sql.q import q_to_ntbl
        
        q_to_ntbl(db, outTbl, sql, api='ogr2ogr')
    
    return outTbl

