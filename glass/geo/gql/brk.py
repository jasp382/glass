"""
Break Operations using SQL Sintax
"""

def split_lines_on_pnt(db, inTbl, pntTbl, outTbl, idlnhPnt,
                       lnhid):
    """
    Split lines on point locations
    """
    
    from glass.sql.i  import cols_name
    from glass.sql.to import q_to_ntbl
    
    # Get cols of lnhTbl
    cols = ", ".join([c for c in cols_name(
        db, inTbl, sanitizeSpecialWords=True, api='psql'
    ) if c != 'geom' and c != idlnhPnt])
    
    # Force MultiLineString to LineString
    sanQ = (
        "SELECT {lid}, {cln}, (ST_Dump(geom)).geom AS geom "
        "FROM {t}) AS mtbl"
    ).format(lid=lnhid, cln=cols, t=inTbl)
    
    # Split Query
    Q = (
        "SELECT {lid}, {cln}, (ST_Dump(geom)).geom AS geom FROM ("
            "SELECT mtbl.{lid}, {cln}, "
            "CASE "
                "WHEN jtbl.{pid} IS NULL THEN mtbl.geom "
                "ELSE ST_Split(mtbl.geom, jtbl.geom) "
            "END AS geom "
            "FROM {lnh_tbl} LEFT JOIN ("
                "SELECT {pid}, ST_Collect(geom) AS geom "
                "FROM {pnt_tbl} "
                "GROUP BY {pid}"
            ") AS jtbl on mtbl.{lid} = jtbl.{pid}"
        ") AS foo"
    ).format(
        lid=lnhid, cln=cols, pid=idlnhPnt,
        lnh_tbl=sanQ, pnt_tbl=pntTbl
    )
    
    # Produce new table and return it
    return q_to_ntbl(db, outTbl, Q)

