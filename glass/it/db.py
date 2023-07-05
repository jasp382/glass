"""
Data to a Relational Database
"""

import os
from glass.pys    import obj_to_lst
from glass.rd     import tbl_to_obj
from glass.wt.sql import df_to_db
from glass.pys    import execmd


def tbl_to_db(tblFile, db, sqlTbl, delimiter=None, encoding_='utf-8',
              sheet=None, isAppend=None, api_db='psql', colsMap=None):
    """
    Table file to Database Table
    
    API's available:
    * psql;
    * sqlite;
    """
    
    from glass.pys.oss import fprop
    
    if os.path.isdir(tblFile):
        from glass.pys.oss import lst_ff
        
        tbls = lst_ff(tblFile)
    
    else:
        tbls = obj_to_lst(tblFile)
    
    outSQLTbl = obj_to_lst(sqlTbl)
    
    RTBL = []
    for i in range(len(tbls)):
        fp = fprop(tbls[i], ['fn', 'ff'])
        ff = fp['fileformat']
        fn = fp['filename']
    
        if ff == '.csv' or ff == '.txt' or ff == '.tsv':
            if not delimiter:
                raise ValueError((
                    "To convert TXT to DB table, you need to give a value for the "
                    "delimiter input parameter"
                ))
        
            __enc = 'utf-8' if not encoding_ else encoding_
        
            data = tbl_to_obj(
                tbls[i], _delimiter=delimiter, encoding_=__enc
            )
    
        elif ff == '.dbf':
            data = tbl_to_obj(tbls[i])
    
        elif ff == '.xls' or ff == '.xlsx':
            data = tbl_to_obj(tbls[i], sheet=sheet)
    
        elif ff == '.ods':
            if not sheet:
                raise ValueError((
                    "To convert ODS to DB table, you need to give a value "
                    "for the sheet input parameter"
                ))
        
            data = tbl_to_obj(tbls[i], sheet=sheet)
    
        else:
            raise ValueError(f'{ff} is not a valid table format!')
        
        if colsMap:
            data.rename(columns=colsMap, inplace=True)
    
        # Send data to database
        out_tbl = fn if not outSQLTbl else outSQLTbl[i] \
            if i+1 <= len(tbls) else fn
        _rtbl = df_to_db(
            db, data, out_tbl,
            append=isAppend, api=api_db
        )
        
        RTBL.append(_rtbl)
    
    return RTBL[0] if len(RTBL) == 1 else RTBL


def xlsx_to_db(xls, db, sheets, apidb='psql'):
    """
    Excel data to database

    API's available:
    * psql;
    * sqlite;
    """

    sheets = obj_to_lst(sheets)

    for s in sheets:
        d = tbl_to_obj(xls, sheet=s)

        df_to_db(db, d, s, api=apidb)
    
    return db


def db_to_db(db_a, db_b, typeDBA, typeDBB):
    """
    All tables in one Database to other database
    
    Useful when we want to migrate a SQLITE DB to a PostgreSQL DB
    
    typesDB options:
    * sqlite
    * psql
    """
    
    from glass.sql.q    import q_to_obj
    from glass.prop.sql import lst_tbl
    from glass.sql.db   import create_db
    
    # List Tables in DB A
    tbls = lst_tbl(db_a, excludeViews=True, api=typeDBA)
    
    # Create database B
    db_b = create_db(db_b, overwrite=False, api=typeDBB)
    
    # Table to Database B
    for tbl in tbls:
        df = q_to_obj(
            db_a, f"SELECT * FROM {tbl}", db_api=typeDBA
        )
        
        df_to_db(db_b, df, tbl, append=None, api=typeDBB)


def tbl_fromdb_todb(from_db, to_db, tables, qForTbl=None, api='pandas'):
    """
    Send PGSQL Tables from one database to other
    """
    
    api = 'pandas' if api != 'pandas' and api != 'psql' else api
    
    tables = obj_to_lst(tables)
    
    if api == 'pandas':
        from glass.sql.q import q_to_obj
    
        for table in tables:
            if not qForTbl:
                tblDf = q_to_obj(
                    from_db, f"SELECT * FROM {table}",
                    db_api='psql'
                )
        
            else:
                if table not in qForTbl:
                    tblDf = q_to_obj(
                        from_db, f"SELECT * FROM {table}",
                        db_api='psql'
                    )
            
                else:
                    tblDf = q_to_obj(from_db, qForTbl[table], db_api='psql')
        
            df_to_db(to_db, tblDf, table, api='psql')
    
    else:
        from glass.pys.oss  import mkdir, del_folder
        from glass.sql.bkup import dump_tbls
        from glass.sql.db   import restore_tbls
        
        tmpFolder = mkdir(
            os.path.dirname(os.path.abspath(__file__)), randName=True
        )
        
        # Dump 
        sqlScript = dump_tbls(from_db, tables, os.path.join(
            tmpFolder, "tables_data.sql"
        ))
            
        # Restore
        restore_tbls(to_db, sqlScript, tables)
        
        del_folder(tmpFolder)


def apndtbl_in_otherdb(db_a, db_b, tblA, tblB, mapCols,
                       geomCol=None, srsEpsg=None, con_a=None, con_b=None):
    """
    Append data of one table to another table in other database.
    """
    
    from glass.sql.q import q_to_obj

    cols = ", ".join(list(mapCols.keys()))
    
    df = q_to_obj(
        db_a, f"SELECT {cols} FROM {tblA}",
        db_api='psql', geomCol=geomCol, epsg=srsEpsg, dbset=con_a
    )
    
    # Change Names
    df.rename(columns=mapCols, inplace=True)
    
    if geomCol:
        for k in mapCols:
            if geomCol == k:
                geomCol = mapCols[k]
                break
    
    # Get Geom Type
    # Send data to other database
    if geomCol and srsEpsg:
        from glass.prop.feat import get_gtype
        
        gType = get_gtype(df, geomCol=geomCol, gisApi='pandas')
        
        df_to_db(
            db_b, df, tblB, append=True, api='psql', epsg=srsEpsg,
            geomType=gType, colGeom=geomCol, dbset=con_b
        )
    
    else:
        df_to_db(db_b, df, tblB, append=True, api='psql', dbset=con_b)
    
    return tblB


def txts_to_db(folder, db, delimiter, __encoding='utf-8', apidb='psql',
               rewrite=None):
    """
    Executes tbl_to_db for every file in a given folder
    
    The file name will be the table name
    """
    
    from glass.pys.oss  import lst_ff, fprop
    from glass.prop.sql import db_exists
    
    if not db_exists(db):
        # Create database
        from glass.sql.db import create_db
        
        create_db(db, api=apidb, overwrite=None)
    
    else:
        if rewrite:
            from glass.sql.db import create_db
            create_db(db, api=db, overwrite=True)
    
    __files = lst_ff(folder, file_format=['.txt', '.csv', '.tsv'])
    
    """
    Send data to DB using Pandas
    """
    for __file in __files:
        tbl_to_db(
            __file, db, fprop(__file, 'fn'),
            delimiter=delimiter, encoding_=__encoding, api_db=apidb
        )


"""
GeoSpatial Data to GeoSpatial Database
"""

def shp_to_psql(dbname, shpData, pgTable=None, api="pandas",
                mapCols=None, srs=None, encoding="UTF-8",
                dbset='default', to_srs=None):
    """
    Send Shapefile to PostgreSQL
    
    if api is equal to "pandas" - GeoPandas API will be used;
    if api is equal to "shp2pgsql" - shp2pgsql tool will be used.
    """
    
    from glass.pys.oss  import fprop
    from glass.prop.prj import get_shp_epsg
    
    # If defined, srsEpsgCode must be a integer value
    if srs and type(srs) != int:
        raise ValueError('srs should be a integer value')
    
    if api == "pandas":
        from glass.rd.shp    import shp_to_obj
        from glass.wt.sql    import df_to_db
        from glass.prop.feat import get_gtype
        from glass.prj.obj   import df_prj
        from glass.pd.geom   import force_multipart
    
    elif api == "shp2pgsql":
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
        get_shp_epsg(i) if not srs else srs for i in shapes
    ]
    
    if None in epsgs:
        raise ValueError((
            "Cannot obtain EPSG code. Use the srs parameter "
            "to specify the EPSG code of your data."
        ))
    
    tables = []
    for _i in range(len(shapes)):
        # Get Table name
        tname = fprop(shapes[_i], 'fn', forceLower=True) if not pgTable else \
            pgTable[_i] if type(pgTable) == list else pgTable if len(shapes) == 1 \
            else pgTable + f'_{str(_i+1)}'
        
        # Import data
        if api == "pandas":
            # SHP to DataFrame
            df = shp_to_obj(shapes[_i])

            # Sanitize columns name
            
            if not mapCols:
                rname = {x : x.lower() for x in df.columns.values}
                
            else:
                rname = {
                    x : mapCols[x].lower() if x in mapCols else \
                    x.lower() for x in df.columns.values
                }

            df.rename(columns=rname, inplace=True)
            
            if "geometry" in df.columns.values:
                geomCol = "geometry"
            
            elif "geom" in df.columns.values:
                geomCol = "geom"
            
            else:
                raise ValueError("No Geometry found in shp")
            
            # Project if necessary
            if to_srs and epsgs[_i] != to_srs:
                df = df_prj(df, to_srs)
            
            # Force multi-geometry if necessary
            gtype = get_gtype(
                df, name=True,
                py_cls=False, gisApi='pandas'
            )
            df = force_multipart(
                df, geomCol,
                epsgs[_i] if not to_srs else to_srs,
                gtype=gtype   
            )
            
            # GeoDataFrame to PSQL
            df_to_db(
                dbname, df, tname, append=True, api='psql',
                epsg=epsgs[_i] if not to_srs else to_srs,
                colGeom=geomCol, geomType=gtype.upper()
            )
        
        else:
            sql_script = os.path.join(
                os.path.dirname(shapes[_i]), f'{tname}.sql'
            )
            
            cmd = (
                f'shp2pgsql -I -s {epsgs[_i]} -W {encoding} '
                f'{shapes[_i]} public.{tname} > {sql_script}'
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

    from glass.sql import psql_cmd
    
    rst_name = os.path.splitext(os.path.basename(rst))[0]
    
    if not sql_script:
        sql_script = os.path.join(os.path.dirname(rst), f'{rst_name}.sql')
    
    cmd = execmd((
        f'raster2pgsql -s {srs} -I -C -M {rst} -F -t 100x100 '
        f'public.{rst_name} > {sql_script}'
    ))
    
    psql_cmd(dbname, sql_script)
    
    return rst_name


def osm_to_psql(osmXml, osmdb, dbsetup='default'):
    """
    Use GDAL to import osmfile into PostGIS database
    """
    
    from glass.cons.psql import con_psql
    from glass.prop.sql  import db_exists

    is_db = db_exists(osmdb, dbset=dbsetup)

    if not is_db:
        from glass.sql.db import create_db

        create_db(osmdb, api='psql', dbset=dbsetup)

    con = con_psql(db_set=dbsetup)
    
    cmd = (
        f"ogr2ogr -f PostgreSQL \"PG:dbname="
        f"'{osmdb}' host='{con['HOST']}' port='{con['PORT']}' "
        f"user='{con['USER']}' password='{con['PASSWORD']}'\" {osmXml} "
        "-lco COLUM_TYPES=other_tags=hstore"
    )
    
    cmdout = execmd(cmd)
    
    return osmdb



def gpkg_lyr_attr_to_psql(gpkg, lyr, col, db, tbl_bname=None):
    """
    GeoPackage layer to PostgreSQL tables

    For a given layer in a GeoPackage, the values in a given column
    will be listen, for each value, the rows with that value
    will be selected and sended to the database
    """

    from glass.cons.psql import con_psql
    from glass.rd.shp    import shp_to_obj

    otbls = {}

    con = con_psql()

    tbl_bname = col if not tbl_bname else tbl_bname

    # Open data
    gdf = shp_to_obj(gpkg, lyr=lyr)

    # Get Attributes
    attrs = gdf[col].unique()

    for attr in attrs:
        ntbl = f"{tbl_bname}_{str(attr)}"

        cmd = (
            'ogr2ogr -f PostgreSQL "PG:dbname='
            f'\'{db}\' host=\'{con["HOST"]}\' port=\'{con["PORT"]}\' '
            f'user=\'{con["USER"]}\' password=\'{con["PASSWORD"]}\'" '
            f'-nln {ntbl} {gpkg} {lyr} '
            f'-where "\\"{col}\\" = {str(attr)}"'
        )

        ocmd = execmd(cmd)

        otbls[attr] = ntbl

    return otbls

