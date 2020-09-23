"""
GeoSpatial Data to GeoSpatial Database
"""

def shp_to_psql(dbname, shpData, pgTable=None, api="pandas",
                mapCols=None, srsEpsgCode=None, encoding="UTF-8",
                dbset='default'):
    """
    Send Shapefile to PostgreSQL
    
    if api is equal to "pandas" - GeoPandas API will be used;
    if api is equal to "shp2pgsql" - shp2pgsql tool will be used.
    """
    
    import os
    from glass.pys.oss     import fprop
    from glass.geo.prop.prj import get_epsg_shp
    
    # If defined, srsEpsgCode must be a integer value
    if srsEpsgCode:
        if type(srsEpsgCode) != int:
            raise ValueError('srsEpsgCode should be a integer value')
    
    if api == "pandas":
        from glass.dct              import tbl_to_obj
        from glass.dct.sql.to       import df_to_db
        from glass.geo.prop.feat import get_gtype
    
    elif api == "shp2pgsql":
        from glass.pys     import execmd
        from glass.sql     import psql_cmd
        from glass.pys.oss import del_file
    
    else:
        raise ValueError(
            'api value is not valid. options are: pandas and shp2pgsql'
        )
    
    # Check if shp is folder
    if os.path.isdir(shpData):
        from glass.pys.oss import lst_ff
        
        shapes = lst_ff(shpData, file_format='.shp')
    
    else:
        from glass.pys import obj_to_lst
        
        shapes = obj_to_lst(shpData)
    
    epsgs = [
        get_epsg_shp(i) for i in shapes
    ] if not srsEpsgCode else [srsEpsgCode]
    
    if None in epsgs:
        raise ValueError((
            "Cannot obtain EPSG code. Use the srsEpsgCode parameter "
            "to specify the EPSG code of your data."
        ))
    
    tables = []
    for _i in range(len(shapes)):
        # Get Table name
        tname = fprop(shapes[_i], 'fn', forceLower=True) if not pgTable else \
            pgTable[_i] if type(pgTable) == list else pgTable if len(shapes) == 1 \
            else pgTable + '_{}'.format(_i+1)
        
        # Import data
        if api == "pandas":
            # SHP to DataFrame
            df = tbl_to_obj(shapes[_i])
            
            if not mapCols:
                df.rename(columns={
                    x : x.lower() for x in df.columns.values
                }, inplace=True)
            else:
                renameD = {
                    x : mapCols[x].lower() if x in mapCols else \
                    x.lower() for x in df.columns.values
                }
                df.rename(columns=renameD, inplace=True)
            
            if "geometry" in df.columns.values:
                geomCol = "geometry"
            
            elif "geom" in df.columns.values:
                geomCol = "geom"
            
            else:
                raise ValueError("No Geometry found in shp")
            
            # GeoDataFrame to PSQL
            df_to_db(
                dbname, df, tname, append=True, api='psql',
                epsg=epsgs[_i] if not srsEpsgCode else srsEpsgCode,
                colGeom=geomCol,
                geomType=get_gtype(shapes[_i], name=True, py_cls=False, gisApi='ogr')
            )
        
        else:
            sql_script = os.path.join(
                os.path.dirname(shapes[_i]), tname + '.sql'
            )
            
            cmd = (
                'shp2pgsql -I -s {epsg} -W {enc} '
                '{shp} public.{name} > {out}'
            ).format(
                epsg=epsgs[_i] if not srsEpsgCode else srsEpsgCode,
                shp=shapes[_i], name=tname, out=sql_script,
                enc=encoding
            )
            
            outcmd = execmd(cmd)
            
            psql_cmd(dbname, sql_script, dbcon=dbset)
            
            del_file(sql_script)
        
        tables.append(tname)
    
    return tables[0] if len(tables) == 1 else tables


def rst_to_psql(rst, srs, dbname, sql_script=None):
    """
    Run raster2pgsql to import a raster dataset into PostGIS Database
    """
    
    import os
    from glass.pys import execmd
    from glass.sql import psql_cmd
    
    rst_name = os.path.splitext(os.path.basename(rst))[0]
    
    if not sql_script:
        sql_script = os.path.join(os.path.dirname(rst), rst_name + '.sql')
    
    cmd = execmd((
        'raster2pgsql -s {epsg} -I -C -M {rfile} -F -t 100x100 '
        'public.{name} > {sqls}'
    ).format(
        epsg=str(srs), rfile=rst, name=rst_name, sqls=sql_script
    ))
    
    psql_cmd(dbname, sql_script)
    
    return rst_name


def osm_to_psql(osmXml, osmdb):
    """
    Use GDAL to import osmfile into PostGIS database
    """
    
    from glass.pys       import execmd
    from glass.cons.psql import con_psql
    from glass.sql.prop     import db_exists

    is_db = db_exists(osmdb)

    if not is_db:
        from glass.sql.db import create_db

        create_db(osmdb, api='psql')

    con = con_psql()
    
    cmd = (
        "ogr2ogr -f PostgreSQL \"PG:dbname='{}' host='{}' port='{}' "
        "user='{}' password='{}'\" {} -lco COLUM_TYPES=other_tags=hstore"
    ).format(
        osmdb, con["HOST"], con["PORT"],
        con["USER"], con["PASSWORD"], osmXml
    )
    
    cmdout = execmd(cmd)
    
    return osmdb

