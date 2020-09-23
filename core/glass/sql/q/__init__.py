"""
Run Queries
"""


def q_to_ntbl(db, outbl, query, ntblIsView=None, api='psql', db__set='default'):
    """
    Create table by query
    
    API's Available:
    * psql;
    * ogr2ogr
    """
    
    if api == 'psql':
        from glass.sql.c import sqlcon
    
        con = sqlcon(db, dbset=db__set)
    
        curs = con.cursor()
    
        _q = "CREATE {} {} AS {}".format(
            "TABLE" if not ntblIsView else "VIEW",
            outbl, query
        )
    
        curs.execute(_q)
    
        con.commit()
        curs.close()
        con.close()
    
    elif api == 'ogr2ogr':
        """
        Execute a SQL Query in a SQLITE Database and store the result in the
        same database. Uses OGR2OGR instead of the regular SQLITE API
        """
        
        from glass.pys  import execmd
        
        cmd = (
            'ogr2ogr -update -append -f "SQLite" {db} -nln "{nt}" '
            '-dialect sqlite -sql "{q}" {db}' 
        ).format(
             db=db, nt=outbl, q=query
        )
        
        outcmd = execmd(cmd)
    
    else:
        raise ValueError('API {} is not available!'.format(api))
    
    return outbl

###############################################################################
###############################################################################


def exec_write_q(db_name, queries, api='psql', dbset='default'):
    """
    Execute Queries and save result in the database
    """
    
    from glass.pys  import obj_to_lst
    
    qs = obj_to_lst(queries)
    
    if not qs:
        raise ValueError("queries value is not valid")
    
    if api == 'psql':
        from glass.sql.c import sqlcon
        
        con = sqlcon(db_name, dbset=dbset)
    
        cs = con.cursor()
    
        for q in qs:
            cs.execute(q)
    
        con.commit()
        cs.close()
        con.close()
    
    elif api == 'sqlite':
        import sqlite3
        
        con = sqlite3.connect(db_name)
        cs  = con.cursor()
        
        for q in qs:
            cs.execute(q)
        
        con.commit()
        cs.close()
        con.close()
    
    else:
        raise ValueError('API {} is not available'.format(api))
