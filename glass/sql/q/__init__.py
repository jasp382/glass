"""
Run Queries
"""


def q_to_obj(dbname, query, db_api='psql', geomCol=None, epsg=None, of='df',
    cols=None, dbset='default'):
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

    import pandas as pd
    import geopandas as gp

    from glass.sql.c import alchemy_engine

    pgengine = alchemy_engine(dbname, dbset=dbset)

    if not query.startswith('SELECT '):
        # Assuming query is a table name
        from glass.pys      import obj_to_lst
        from glass.prop.sql import cols_name

        cols = cols_name(dbname, query) if not cols else \
            obj_to_lst(cols)
        
        qcols = ", ".join([f"{query}.{i} AS {i}" for i in cols])

        query = f"SELECT {qcols} FROM {query}"
    
    if not geomCol:
        df = pd.read_sql(query, pgengine, columns=None)
    
    else:
        if db_api == 'psql':
        
            df = gp.GeoDataFrame.from_postgis(
                query, pgengine, geom_col=geomCol,
                crs=f"EPSG:{str(epsg)}" if epsg else None
            )
        
        else:
            raise ValueError('Exporting geometries only works for psql API')
    
    if of == 'dict':
        df = df.to_dict(orient="records")
    
    return df


###############################################################################
###############################################################################


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

        t = "TABLE" if not ntblIsView else "VIEW"
    
        _q = f"CREATE {t} {outbl} AS {query}"

        curs.execute(_q)
    
        con.commit()
        curs.close()
        con.close()
    
    elif api == 'ogr2ogr':
        """
        Execute a SQL Query in a SQLITE Database and store the result in the
        same database. Uses OGR2OGR instead of the regular SQLITE API
        """
        
        from glass.pys import execmd
        
        cmd = (
            f'ogr2ogr -update -append -f "SQLite" {db} -nln "{outbl}" '
            f'-dialect sqlite -sql "{query}" {db}' 
        )
        
        outcmd = execmd(cmd)
    
    else:
        raise ValueError(f'API {api} is not available!')
    
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
        raise ValueError(f'API {api} is not available')
