import psycopg2

import pandas as pd
import geopandas as gp

from osgeo import osr

import xml.etree.cElementTree as ET

from sqlalchemy        import create_engine

from api.settings import GEOSERVER_CON, DATABASES


def alchemy_engine(db):
    """
    Get engine that could be used for pandas to import data into
    PostgreSQL
    """

    cp = DATABASES['default']
    
    return create_engine((
        f'postgresql+psycopg2://{cp["USER"]}:{cp["PASSWORD"]}'
        f'@{cp["HOST"]}:{cp["PORT"]}/{db}'
    ))


def sqlcon(db):
    """
    Connect to PostgreSQL Database
    """

    conparam = DATABASES['default']
    
    try:
        if not db:
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            c = psycopg2.connect(
                user=conparam["USER"], password=conparam["PASSWORD"],
                host=conparam["HOST"], port=conparam["PORT"]
            )
            c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    
        else:
            c = psycopg2.connect(
                database=db, user=conparam["USER"],
                password=conparam["PASSWORD"], host=conparam["HOST"],
                port=conparam["PORT"],
            )
        
        return c
    
    except psycopg2.Error as e:
        raise ValueError(str(e))


def q_to_obj(dbname, query, geomCol=None, epsg=None):
    """
    Query database and convert data to Pandas Dataframe/GeoDataFrame

    output format options ("of" parameter):
    * df (Pandas Dataframe);
    * dict (Python Dict);
    """

    pgengine = alchemy_engine(dbname)
    
    if not geomCol:
        df = pd.read_sql(query, pgengine, columns=None)
    
    else:
        df = gp.GeoDataFrame.from_postgis(
            query, pgengine, geom_col=geomCol,
            crs=f"EPSG:{str(epsg)}" if epsg else None
        )
    
    return df


def lst_views(db):
    """
    List Views in database
    """

    db = DATABASES['default']['NAME']
    
    views = q_to_obj(db, (
        "SELECT table_name FROM information_schema.views "
        f"WHERE table_schema='public'"
    ))
    
    return views.table_name.tolist()


def q_to_ntbl(db, outbl, query, ntblIsView=None):
    """
    Create table by query
    """
    
    con = sqlcon(db)
    
    curs = con.cursor()

    tv = "TABLE" if not ntblIsView else "VIEW"
    
    _q = f"CREATE {tv} {outbl} AS {query}"
    
    curs.execute(_q)
    
    con.commit()
    curs.close()
    con.close()
    
    return outbl

