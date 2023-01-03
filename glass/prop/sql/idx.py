"""
Geometries Indexes
"""

def idx_for_geom(db_name, table, geomCol):
    """
    Add index to Geometry
    """
    
    from glass.sql.c import sqlcon
    
    con = sqlcon(db_name)
    cursor = con.cursor()
    
    cursor.execute((
        "CREATE INDEX {tbl}_{col}_idx ON {tbl} USING gist ({col})"
    ).format(tbl=table, col=geomCol))
    
    con.commit()
    
    cursor.close()
    con.close()
    
    return table

