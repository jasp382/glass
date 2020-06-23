"""
Database data to Python Object/Array
"""

def q_to_obj(dbname, query, db_api='psql', geomCol=None, epsg=None, of='df',
    cols=None):
    """
    Query database and convert data to Pandas Dataframe/GeoDataFrame
    
    API's Available:
    * psql;
    * sqlite;
    * mysql;

    output format options ("of" parameter):
    * df (Pandas Dataframe);
    * dict (Python Dict);
    """

    if not query.startswith('SELECT '):
        # Assuming query is a table name
        from glass.pyt   import obj_to_lst
        from glass.sql.i import cols_name

        cols = cols_name(dbname, query) if not cols else \
            obj_to_lst(cols)

        query = "SELECT {} FROM {}".format(
            ", ".join(["{t}.{c} AS {c}".format(
                t=query, c=i
            ) for i in cols]), query
        )
    
    if not geomCol:
        import pandas
        from glass.sql.c import alchemy_engine
    
        pgengine = alchemy_engine(dbname, api=db_api)
    
        df = pandas.read_sql(query, pgengine, columns=None)
    
    else:
        from geopandas  import GeoDataFrame
        from glass.sql.c import sqlcon
        
        con = sqlcon(dbname, sqlAPI='psql')
        
        df = GeoDataFrame.from_postgis(
            query, con, geom_col=geomCol,
            crs="epsg:{}".format(str(epsg)) if epsg else None
        )
    
    if of == 'dict':
        df = df.to_dict(orient="records")
    
    return df


"""
Dump Databases and their tables
"""

def dump_db(db, outSQL, api='psql'):
    """
    DB to SQL Script
    """
    
    from glass.pyt import execmd
    
    if api == 'psql':
        from glass.cons.psql import con_psql

        condb = con_psql()

        cmd = "pg_dump -U {} -h {} -p {} -w {} > {}".format(
            condb["USER"], condb["HOST"], condb["PORT"],
            db, outSQL
        )
    
    elif api == 'mysql':
        from glass.cons.mysql import con_mysql

        condb = con_mysql()

        cmd = (
            "mysqldump -u {} --port {} -p{} --host {} "
            "{} > {}"
        ).format(
            condb["USER"], condb["PORT"], condb["PASSWORD"],
            condb["HOST"], db, outSQL
        )
    
    else:
        raise ValueError('{} API is not available'.format(api))
    
    outcmd = execmd(cmd)
    
    return outSQL


def dump_tbls(db, tables, outsql, startWith=None):
    """
    Dump one table into a SQL File
    """
    
    from glass.pyt       import execmd
    from glass.pyt       import obj_to_lst
    from glass.cons.psql import con_psql
    
    tbls = obj_to_lst(tables)
    
    if startWith:
        from glass.sql.i import lst_tbl
        
        db_tbls = lst_tbl(db, api='psql')
        
        dtbls = []
        for t in db_tbls:
            for b in tbls:
                if t.startswith(b):
                    dtbls.append(t)
        
        tbls = dtbls
    
    condb = con_psql()
    
    outcmd = execmd((
        "pg_dump -Fc -U {user} -h {host} -p {port} "
        "-w {tbl} {db} > {out}"
    ).format(
        user=condb["USER"], host=condb["HOST"],
        port=condb["PORT"], db=db, out=outsql,
        tbl=" ".join(["-t {}".format(t) for t in tbls])
    ))
    
    return outsql

