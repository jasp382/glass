"""
Deal with DBMS Databases
"""

def create_pgdb(newdb, overwrite=True, use_template=True, dbset='default',
    geosupport=None, schema={}):
    """
    Create Relational Database
    """
    
    from glass.sql.c     import sqlcon
    from glass.cons.psql import con_psql
    from glass.prop.sql  import lst_db

    conparam = con_psql(db_set=dbset)
    
    dbs = lst_db()
    
    con = sqlcon(None, dbset=dbset)
    cs = con.cursor()
    
    if newdb in dbs and overwrite:
        cs.execute(f"DROP DATABASE {newdb};")
    
    tmplt = f" TEMPLATE={conparam['TEMPLATE']}" \
        if "TEMPLATE" in conparam and use_template else ""
    
    cs.execute(f"CREATE DATABASE {newdb}{tmplt};")

    if not use_template and geosupport:
        ge = [
            'postgis', 'hstore', 'postgis_topology', 'postgis_raster',
            'pgrouting'
        ]
        for e in ge:
            cs.execute(f"CREATE EXTENSION {e};")
    
    cs.close()
    con.close()
    
    return newdb


def create_sqlitedb(dbpath, overwrite=None):
    """
    Create a new sqlite DB
    """

    import os, sqlite3
        
    try:
        if os.path.exists(dbpath) and overwrite:
            from glass.pys.oss import del_file
            del_file(dbpath)
            
        conn = sqlite3.connect(dbpath)
    
    except Error as e:
        print(e)
    finally:
        conn.close()


"""
Delete Databases
"""

def drop_db(database):
    """
    Delete PostgreSQL database
    
    Return 0 if the database does not exist
    """

    from glass.sql.c    import sqlcon
    from glass.prop.sql import lst_db
    
    databases = lst_db()
    
    if database not in databases: return 0
    
    con = sqlcon(None)
    cursor = con.cursor()
    
    try:
        cursor.execute(f"DROP DATABASE {database};")
    except:
        cursor.execute((
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{database}';"
        ))
        
        cursor.execute(f"DROP DATABASE {database};")
        
    cursor.close()
    con.close()

    return 1

def drop_db_like(db_like):
    """
    Drop databases with name like db_like
    """

    from glass.pys import execmd

    rcmd = execmd((
        "sudo -u postgres psql -c \"copy(SELECT datname FROM "
        f"pg_database WHERE datname LIKE '{db_like}') "
        "to stdout\" | while read line; do; sudo -u postgres "
        "-c \"DROP DATABASE $line;\"; done"
    ))

    return rcmd


"""
Restore Data
"""

def restore_db(db, sqlScript, api='psql', dbset=None):
    """
    Restore Database using SQL Script
    """
    
    from glass.pys import execmd
    
    if api == 'psql':
        from glass.cons.psql import con_psql

        condb = con_psql(db_set='default' if not dbset else dbset)

        h, u, p = condb['HOST'], condb['USER'], condb['PORT']

        cmd = f'psql -h {h} -U {u} -p {p} -w {db} < {sqlScript}'
    
    elif api == 'mysql':
        from glass.cons.mysql import con_mysql

        condb = con_mysql()

        u, p = condb['USER'], condb['PASSWORD']

        cmd = f'mysql -u {u} -p{p} {db} < {sqlScript}'
    
    else:
        raise ValueError(f'{api} API is not available')
    
    outcmd = execmd(cmd)
    
    return db


def restore_tbls(dbn, sql, tablenames=None, dbset='default'):
    """
    Restore tables from a sql Script
    
    TODO: add mysql option
    """
    
    from glass.pys       import execmd
    from glass.cons.psql import con_psql
    from glass.pys       import obj_to_lst

    condb = con_psql(db_set=dbset)
    
    tbls = obj_to_lst(tablenames)

    tblstr = "" if not tablenames else \
        " ".join([f"-t {t}" for t in tbls])
    
    tblStr = "" if not tablenames else f" {tblstr}"

    u, h, p = condb["USER"], condb["HOST"], condb["PORT"]
    
    outcmd = execmd((
        f"pg_restore -U {u} -h {h} -p {p} "
        f"-w{tblStr} -d {dbn} {sql}"
    ))
    
    return tablenames


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
    from glass.pys.oss  import fprop, del_file
    from glass.sql      import psql_cmd
    from glass.prop.sql import db_exists, lst_tbl
    from glass.sql.db   import create_pgdb, drop_db
    from glass.sql.tbl  import rename_tbl, tbls_to_tbl
    from glass.sql.bkup import dump_tbls
    from glass.sql.db   import restore_tbls
    from glass.sql.tbl  import distinct_to_table, del_tables
    
    # Prepare database
    fdb = fprop(destinationDb, ['fn', 'ff'])
    if fdb['fileformat'] != '':
        if fdb['fileformat'] == '.sql':
            newdb = create_pgdb(fdb['filename'], overwrite=None)
            
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
            create_pgdb(destinationDb, overwrite=None)
    
    # Check if dbs is a list or a dir
    if type(dbs) == list:
        dbs = dbs
    elif os.path.isdir(dbs):
        # list SQL files
        from glass.pys.oss import lst_ff
        
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
            create_pgdb(DB_NAME, overwrite=True)
        
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
            tn = f"{tbls[t]}_{str(i)}"
            if tbls[t] not in TABLES:
                TABLES[tbls[t]] = [tn]
            
            else:
                TABLES[tbls[t]].append(tn)
        
        # Dump Tables
        SQL_DUMP = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            f'tbl_{DB_NAME}.sql'
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
        NEW_TBL = f"{tbl}_{max_len}"
        rename_tbl(destinationDb, {tbl : NEW_TBL})
        
        TABLES[tbl].append(NEW_TBL)
        
        # Union
        tbls_to_tbl(destinationDb, TABLES[tbl], tbl + '_tmp')
        
        # Group By
        distinct_to_table(destinationDb, tbl + '_tmp', tbl, cols=None)
        
        # Drop unwanted tables
        del_tables(destinationDb, TABLES[tbl] + [tbl + '_tmp'])
    
    return destinationDb

