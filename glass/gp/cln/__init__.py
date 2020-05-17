"""
Clean Geometries
"""

def remove_deadend(inShp, outShp, db=None):
    """
    Remove deadend
    """
    
    from glass.pys.oss    import fprop
    from glass.sql.db     import create_pgdb
    from glass.it.db      import shp_to_psql
    from glass.gp.cln.sql import rm_deadend
    from glass.it.shp     import dbtbl_to_shp
    
    # Create DB
    if not db:
        db = create_pgdb(fprop(inShp, 'fn', forceLower=True))
    
    else:
        from glass.prop.sql import db_exists
        isDb = db_exists(db)
        
        if not isDb:
            create_pgdb(db)
    
    # Send data to Database
    inTbl = shp_to_psql(db, inShp, api="shp2pgsql", encoding="LATIN1")
    
    # Produce result
    out_tbl = rm_deadend(db, inTbl, fprop(
        outShp, 'fn', forceLower=True))
    
    # Export result
    return dbtbl_to_shp(
        db, out_tbl, "geom", outShp, inDB='psql',
        tableIsQuery=None, api="pgsql2shp"
    )

