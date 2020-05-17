"""
Generalization tools using SpatiaLite
"""

def st_dissolve(db, table, geomColumn, outTable, whrClause=None,
                diss_cols=None, outTblIsFile=None, api='sqlite'):
    """
    Dissolve a Polygon table
    """
    
    from glass.pys import obj_to_lst
    
    diss_cols = obj_to_lst(diss_cols) if diss_cols else None
    geomcol = "geometry" if api == 'sqlite' else 'geom'
    
    sql = (
        "SELECT{selCols} ST_UnaryUnion(ST_Collect({geom})) AS {gout} "
        "FROM {tbl}{whr}{grpBy}"
    ).format(
        selCols="" if not diss_cols else " {},".format(", ".join(diss_cols)),
        geom=geomColumn, tbl=table,
        whr="" if not whrClause else " WHERE {}".format(whrClause),
        grpBy="" if not diss_cols else " GROUP BY {}".format(
            ", ".join(diss_cols)
        ), gout=geomcol
    )
    
    if outTblIsFile:
        if api == 'sqlite':
            from glass.geo.df.attr import sel_by_attr
            
            sel_by_attr(db, sql, outTable, api_gis='ogr')
        
        elif api == 'psql':
            from glass.dct.geo.toshp.db import dbtbl_to_shp
            
            dbtbl_to_shp(
                db, table, geomColumn, outTable, api='pgsql2shp',
                tableIsQuery=True
            )
    
    else:
        from glass.sql.q import q_to_ntbl
        
        q_to_ntbl(
            db, outTable, sql, api='ogr2ogr' if api == 'sqlite' else 'psql'
        )
    
    return outTable

