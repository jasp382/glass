"""
Run Queries
"""

def exec_write_q(db_name, queries, api='psql'):
    """
    Execute Queries and save result in the database
    """
    
    from glass.pyt import obj_to_lst
    
    qs = obj_to_lst(queries)
    
    if not qs:
        raise ValueError("queries value is not valid")
    
    if api == 'psql':
        from glass.sql.c import sqlcon
        
        con = sqlcon(db_name)
    
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
