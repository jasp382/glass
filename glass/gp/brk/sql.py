"""
Break Operations using SQL Sintax
"""

def split_lines_on_pnt(db, inTbl, pntTbl, outTbl, idlnhPnt,
                       lnhid):
    """
    Split lines on point locations
    """
    
    from glass.prop.sql import cols_name
    from glass.sql.q    import q_to_ntbl
    
    # Get cols of lnhTbl
    cols = ", ".join([c for c in cols_name(
        db, inTbl, sanitizeSpecialWords=True, api='psql'
    ) if c != 'geom' and c != idlnhPnt])
    
    # Force MultiLineString to LineString
    sanQ = (
        f"SELECT {lnhid}, {cols}, (ST_Dump(geom)).geom AS geom "
        f"FROM {inTbl}) AS mtbl"
    )
    
    # Split Query
    Q = (
        f"SELECT {lnhid}, {cols}, (ST_Dump(geom)).geom AS geom FROM ("
            f"SELECT mtbl.{lnhid}, {cols}, "
            f"CASE "
                f"WHEN jtbl.{idlnhPnt} IS NULL THEN mtbl.geom "
                "ELSE ST_Split(mtbl.geom, jtbl.geom) "
            "END AS geom "
            f"FROM {sanQ} LEFT JOIN ("
                f"SELECT {idlnhPnt}, ST_Collect(geom) AS geom "
                f"FROM {pntTbl} "
                f"GROUP BY {idlnhPnt}"
            f") AS jtbl on mtbl.{lnhid} = jtbl.{idlnhPnt}"
        ") AS foo"
    )
    
    # Produce new table and return it
    return q_to_ntbl(db, outTbl, Q)

