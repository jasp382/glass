""""
Get Information about SQL database or database data
"""

from glass.ng.sql.c import sqlcon

"""
Info about databases
"""

def lst_db(dbset=None):
    """
    List all PostgreSQL databases
    """
    
    con = sqlcon(None, dbset='default' if not dbset else dbset)
    
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    return [d[0] for d in cursor.fetchall()]


def db_exists(db, dbset='default'):
    """
    Database exists
    """

    con = sqlcon(None, dbset=dbset)
        
    cursor = con.cursor()
    
    cursor.execute("SELECT datname FROM pg_database")
    
    dbs = [d[0] for d in cursor.fetchall()]
    
    con.close()
    
    return 1 if db in dbs else 0


"""
Tables Info
"""

def lst_views(db, schema='public', basename=None, dbset='default'):
    """
    List Views in database
    """
    
    from glass.pys      import obj_to_lst
    from glass.ng.sql.q import q_to_obj
    
    basename = obj_to_lst(basename)
    
    basenameStr = "" if not basename else "{}".format(
        " OR ".join(["{} LIKE '%%{}%%'".format(
            "table_name", b
        ) for b in basename])
    )
    
    views = q_to_obj(db, (
        "SELECT table_name FROM information_schema.views "
        "WHERE table_schema='{}'{}"
    ).format(schema, "" if not basename else " AND ({})".format(
        basenameStr
    )), db_api='psql', dbset=dbset)
    
    return views.table_name.tolist()


def lst_tbl(db, schema='public', excludeViews=None, api='psql',
            basename=None, db_set='default'):
    """
    list tables in a database
    
    API's Available:
    * psql;
    * sqlite;
    * mysql;
    """
    
    from glass.pys import obj_to_lst
    
    basename = obj_to_lst(basename)
    
    basenameStr = "" if not basename else "{}".format(
        " OR ".join(["{} LIKE '%%{}%%'".format(
            "table_name" if api == 'psql' else "name", b
        ) for b in basename])
    )
    
    if api == 'psql':
        from glass.ng.sql.q import q_to_obj
        
        Q = (
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema='{}'{}"
        ).format(schema, "" if not basename else " AND ({})".format(
            basenameStr))
    
        tbls = q_to_obj(db, Q, db_api='psql', dbset=db_set)
    
        if excludeViews:
            views = lst_views(db, schema=schema, dbset=db_set)
        
            __tbls = [i for i in tbls.table_name.tolist() if i not in views]
    
        else:
            __tbls = tbls.table_name.tolist()
    
    elif api == 'sqlite':
        """
        List tables in one sqliteDB
        """
        
        import sqlite3
        
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        
        tables = cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'{};".format(
                "" if not basename else " AND ({})".format(basenameStr)
            )
        )
        
        __tbls = [n[0] for n in tables]
        cursor.close()
        conn.close()
    
    elif api == 'mysql':
        """
        List Tables in MySQL Database
        """
        
        from glass.ng.sql.c import alchemy_engine
        
        c = alchemy_engine(db, api='mysql')
        
        __tbls = c.table_names()
    
    else:
        raise ValueError('API {} is not available!'.format(api))
    
    return __tbls


"""
Counting in table
"""

def row_num(db, table, where=None, api='psql', dbset='default'):
    """
    Return the number of rows in Query
    
    API's Available:
    * psql;
    * sqlite;
    """
    
    from glass.ng.sql.q import q_to_obj
    
    if not table.startswith('SELECT '):
        Q = "SELECT COUNT(*) AS nrows FROM {}{}".format(
            table,
            "" if not where else " WHERE {}".format(where)
        )
    else:
        Q = "SELECT COUNT(*) AS nrows FROM ({}) AS foo".format(table)
    
    d = q_to_obj(db, Q, db_api=api, dbset=dbset)
    
    return int(d.iloc[0].nrows)


"""
Info about fields in table
"""

def cols_name(dbname, table, sanitizeSpecialWords=True, api='psql', dbset='default'):
    """
    Return the columns names of a table in one Database
    """
    
    if api == 'psql':
        c = sqlcon(dbname, sqlAPI='psql', dbset=dbset)
    
        cursor = c.cursor()
        cursor.execute("SELECT * FROM {} LIMIT 1;".format(table))
        colnames = [desc[0] for desc in cursor.description]
    
        if sanitizeSpecialWords:
            from glass.cons.psql import PG_SPECIAL_WORDS
    
            for i in range(len(colnames)):
                if colnames[i] in PG_SPECIAL_WORDS:
                    colnames[i] = '"{}"'.format(colnames[i])
    
    elif api == 'sqlite':
        import sqlite3
        
        con = sqlite3.connect(dbname)
        
        cursor = con.execute("SELECT * FROM {} LIMIT 1".format(table))
        
        colnames = list(map(lambda x: x[0], cursor.description))
    
    elif api == 'mysql':
        from glass.ng.sql.q import q_to_obj
        
        data = q_to_obj(
            dbname, "SELECT * FROM {} LIMIT 1".format(table), db_api='mysql')
        
        colnames = data.columns.values
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return colnames


def cols_type(dbname, table, sanitizeColName=True, pyType=True):
    """
    Return columns names and types of a PostgreSQL table
    """
    
    from glass.cons.psql import PG_SPECIAL_WORDS, map_psqltypes
    
    c = sqlcon(dbname)
    
    cursor = c.cursor()
    cursor.execute("SELECT * FROM {} LIMIT 50;".format(table))
    coltypes = {
        desc[0]: map_psqltypes(
            desc[1], python=pyType) for desc in cursor.description
    }
    
    if sanitizeColName:
        for name in coltypes:
            if name in PG_SPECIAL_WORDS:
                n = '"{}"'.format(name)
                coltypes[n] = coltypes[name]
                del coltypes[name]
    
    return coltypes


"""
Table Meta
"""

def check_last_id(db, pk, table):
    """
    Check last ID of a given table
    
    return 0 if there is no data
    """
    
    from glass.ng.sql.q import q_to_obj
    
    q = "SELECT MAX({}) AS fid FROM {}".format(pk, table)
    d = q_to_obj(db, q, db_api='psql').fid.tolist()
    
    if not d[0]:
        return 0
    else:
        return d[0]

