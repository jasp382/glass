"""
Deal with DBMS Databases
"""

def create_db(newdb, overwrite=True, api='psql', use_template=True):
    """
    Create Relational Database
    
    APIS Available:
    * psql;
    * sqlite;
    """
    
    if api == 'psql':
        from glass.sql.c     import sqlcon
        from glass.sql.i     import lst_db
        from glass.cons.psql import con_psql

        conparam = con_psql()
    
        dbs = lst_db()
    
        con = sqlcon(None, sqlAPI='psql')
        cs = con.cursor()
    
        if newdb in dbs and overwrite:
            cs.execute("DROP DATABASE {};".format(newdb))
    
        cs.execute("CREATE DATABASE {}{};".format(
            newdb, " TEMPLATE={}".format(conparam["TEMPLATE"]) \
                if "TEMPLATE" in conparam and use_template else ""
            )
        )
    
        cs.close()
        con.close()
    
    elif api == 'sqlite':
        import os
        import sqlite3
        
        try:
            if os.path.exists(newdb) and overwrite:
                from glass.pyt.oss import del_file
                del_file(newdb)
            
            conn = sqlite3.connect(newdb)
        except Error as e:
            print(e)
        finally:
            conn.close()
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return newdb


"""
Delete Databases
"""

def drop_db(database):
    """
    Delete PostgreSQL database
    
    Return 0 if the database does not exist
    """
    
    from glass.sql.c import sqlcon
    from glass.sql.i import lst_db
    
    databases = lst_db()
    
    if database not in databases: return 0
    
    con = sqlcon(None, sqlAPI='psql')
    cursor = con.cursor()
    
    try:
        cursor.execute("DROP DATABASE {};".format(database))
    except:
        cursor.execute((
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = '{}';"
        ).format(database))
        
        cursor.execute("DROP DATABASE {};".format(database))
        
    cursor.close()
    con.close()

    return 1


"""
Merge Databases
"""

def merge_dbs(destinationDb, dbs,
              tbls_to_merge=None, ignoretbls=None):
    """
    Put several database into one
    
    For now works only with PostgreSQL
    """
    
    import os
    from glass.pyt.oss import fprop, del_file
    from glass.sql     import psql_cmd
    from glass.sql.i   import db_exists, lst_tbl
    from glass.sql.db  import create_db, drop_db
    from glass.sql.tbl import rename_tbl, tbls_to_tbl
    from glass.sql.fm  import dump_tbls
    from glass.sql.to  import restore_tbls
    from glass.sql.tbl import distinct_to_table, del_tables
    
    # Prepare database
    fdb = fprop(destinationDb, ['fn', 'ff'])
    if fdb['fileformat'] != '':
        if fdb['fileformat'] == '.sql':
            newdb = create_db(fdb['filename'], 
                overwrite=None, api='psql')
            
            psql_cmd(newdb, destinationDb)
            
            destinationDb = newdb
        
        else:
            raise ValueError((
                'destinationDb is a file but is not correct. The file must be'
                ' a SQL Script'
            ))
    
    else:
        if os.path.isdir(destinationDb):
            raise ValueError(
                'destinationdb is a dir. It must be a DB name or a SQL Script'
            )
        
        # Check if destination db exists
        if not db_exists(destinationDb):
            create_db(destinationDb, overwrite=None, api='psql')
    
    # Check if dbs is a list or a dir
    if type(dbs) == list:
        dbs = dbs
    elif os.path.isdir(dbs):
        # list SQL files
        from glass.pyt.oss import lst_ff
        
        dbs = lst_ff(dbs, file_format='.sql')
    
    else:
        raise ValueError(
            '''
            dbs value should be a list with paths 
            to sql files or a dir with sql files inside
            '''
        )
    
    TABLES = {}
    
    for i in range(len(dbs)):
        # Check if DB is a file or a db
        fp = fprop(dbs[i], ['fn', 'ff'])
        DB_NAME = fp['filename']

        if fp['fileformat'] == '.sql':
            # Create DB        
            create_db(DB_NAME, overwrite=True, api='psql')
        
            # Restore DB
            psql_cmd(DB_NAME, dbs[i])
        
        # List Tables
        if not tbls_to_merge:
            tbls__ = lst_tbl(DB_NAME, excludeViews=True, api='psql')

            tbls = tbls__ if not ignoretbls else [t for t in tbls__ if t not in ignoretbls]
        else:
            tbls   = tbls_to_merge
        
        # Rename Tables
        newTbls = rename_tbl(DB_NAME, {tbl : "{}_{}".format(
            tbl, str(i)) for tbl in tbls})
        
        for t in range(len(tbls)):
            if tbls[t] not in TABLES:
                TABLES[tbls[t]] = ["{}_{}".format(tbls[t], str(i))]
            
            else:
                TABLES[tbls[t]].append("{}_{}".format(tbls[t], str(i)))
        
        # Dump Tables
        SQL_DUMP = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'tbl_{}.sql'.format(DB_NAME)
        ); dump_tbls(DB_NAME, newTbls, SQL_DUMP)
        
        # Restore Tables in the destination Database
        restore_tbls(destinationDb, SQL_DUMP, newTbls)
        
        # Delete Temp Database
        if fp['fileformat'] == '.sql':
            drop_db(DB_NAME)
        
        # Delete SQL File
        del_file(SQL_DUMP)
    
    # Union of all tables
    max_len = max([len(TABLES[t]) for t in TABLES])
    
    for tbl in TABLES:
        # Rename original table
        NEW_TBL = "{}_{}".format(tbl, max_len)
        rename_tbl(destinationDb, {tbl : NEW_TBL})
        
        TABLES[tbl].append(NEW_TBL)
        
        # Union
        tbls_to_tbl(destinationDb, TABLES[tbl], tbl + '_tmp')
        
        # Group By
        distinct_to_table(destinationDb, tbl + '_tmp', tbl, cols=None)
        
        # Drop unwanted tables
        del_tables(destinationDb, TABLES[tbl] + [tbl + '_tmp'])
    
    return destinationDb

