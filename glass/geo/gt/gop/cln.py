"""
Clean Geometries
"""

def remove_deadend(inShp, outShp, db=None):
    """
    Remove deadend
    """
    
    from glass.pyt.oss     import fprop
    from glass.sql.db      import create_db
    from glass.geo.gql.to      import shp_to_psql
    from glass.geo.gql.cln     import rm_deadend
    from glass.geo.gt.toshp.db import dbtbl_to_shp
    
    # Create DB
    if not db:
        db = create_db(fprop(inShp, 'fn', forceLower=True), api='psql')
    
    else:
        from glass.sql.i import db_exists
        isDb = db_exists(db)
        
        if not isDb:
            create_db(db, api='psql')
    
    # Send data to Database
    inTbl = shp_to_psql(db, inShp, api="shp2pgsql", encoding="LATIN1")
    
    # Produce result
    out_tbl = rm_deadend(db, inTbl, fprop(
        outShp, 'fn', forceLower=True))
    
    # Export result
    return dbtbl_to_shp(
        db, out_tbl, "geom", outShp, inDB='psql', tableIsQuery=None,
        api="pgsql2shp"
    )

