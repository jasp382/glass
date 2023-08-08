"""
Data to a Relational Database
"""


def df_to_db(db, df, table, append=None, api='psql',
             epsg=None, geomType=None, colGeom='geometry', dbset='default'):
    """
    Pandas Dataframe/GeoDataFrame to PGSQL table
    
    API options:
    * psql;
    * sqlite
    """
    
    if api != 'psql' and api != 'sqlite':
        raise ValueError(f'API {api} is not available')
    
    from glass.sql.c import alchemy_engine
    
    pgengine = alchemy_engine(db, api=api, dbset=dbset)
    
    if epsg and geomType:
        from geoalchemy2 import Geometry, WKTElement

        newdf = df.copy()
        
        newdf["geom"] = newdf[colGeom].apply(
            lambda x : WKTElement(x.wkt, srid=epsg)
        )
        
        if colGeom != 'geom':
            newdf.drop(colGeom, axis=1, inplace=True)
        
        newdf.to_sql(
            table, pgengine,
            if_exists='replace' if not append else 'append',
            index=False, dtype={"geom" : Geometry(geomType, srid=epsg)}
        )
    
    else:
        df.to_sql(
            table, pgengine,
            if_exists='replace' if not append else 'append',
            index=False
        )
    
    return table

