"""
Data to a Relational Database
"""

from glass.sql.c import alchemy_engine


def df_to_db(db, df, table, append=None, api='psql',
             epsg=None, geom_type=None, col_geom=None, dbset='default'):
    """
    Pandas Dataframe/GeoDataFrame to PGSQL table
    
    API options:
    * psql;
    * sqlite
    """

    from geoalchemy2 import Geometry, WKTElement

    from glass.prop.feat import get_gtype
    from glass.pd.geom   import force_multipart
    from glass.prop.prj  import df_epsg
    
    if api != 'psql' and api != 'sqlite':
        raise ValueError(f'API {api} is not available')
    
    if col_geom:
        epsg = df_epsg(df, col_geom) if not epsg else epsg
    
        # For geometry if necessary
        gtype = get_gtype(
            df, name=True, geomCol=col_geom,
            py_cls=False, gisApi='pandas'
        ) if not geom_type else geom_type

        df = force_multipart(df, col_geom, epsg, gtype=gtype)

    
    pgengine = alchemy_engine(db, api=api, dbset=dbset)

    newdf = df.copy()
    
    if col_geom:
        newdf[col_geom] = newdf[col_geom].apply(
            lambda x : WKTElement(x.wkt, srid=epsg)
        )
        
        newdf.to_sql(
            table, pgengine,
            if_exists='replace' if not append else 'append',
            index=False, dtype={col_geom : Geometry(gtype.upper(), srid=epsg)}
        )
    
    else:
        newdf.to_sql(
            table, pgengine,
            if_exists='replace' if not append else 'append',
            index=False
        )
    
    return table

