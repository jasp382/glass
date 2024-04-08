"""
Data to a Relational Database
"""

import os
from multiprocessing import Pool, cpu_count
from tqdm import tqdm


from glass.pys    import obj_to_lst, execmd
from glass.rd     import tbl_to_obj
from glass.wt.sql import df_to_db
from glass.pys.oss import fprop
from glass.sql.c import alchemy_engine


def tbl_to_db(tblFile, db, sqlTbl, delimiter=None, encoding_='utf-8',
              sheet=None, isAppend=None, api_db='psql', colsMap=None, mantain_map_cols=None):
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
            if mantain_map_cols:
                data.drop(
                    [c for c in data.columns.values if c not in colsMap],
                    axis=1, inplace=True
                )
            
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


def import_excel(_t, _db, otbl, _cols=None, chunksize=5000):
    try:
        pgengine = alchemy_engine(_db, api='psql', dbset='default')

        df = tbl_to_obj(_t, fields=_cols)

        df.to_sql(
            otbl, con=pgengine,
            if_exists="append",
            index=False,
            method='multi',
            chunksize=chunksize
        )

        return f"✅ {fprop(_t, 'fn')} importado ({df.shape[0]} linhas)"
        
    except Exception as e:
        raise ValueError(e)


def multixlsx_to_onetable(tbls:list[str], db:str, otbl:str, cols=None, chunks=5000):
    """
    Thousands of xlsx. files to a database
    """

    workers = max(1, int(cpu_count() / 2))

    if not len(tbls):
        return []

    pgcon = alchemy_engine(db, api='psql', dbset='default')
    _df = tbl_to_obj(tbls[0], fields=cols)

    _df.to_sql(
        otbl, con=pgcon,
        if_exists="replace",
        index=False,
        method='multi',
        chunksize=chunks
    )

    args = [(t, db, otbl, cols, chunks) for t in tbls[1:]]

    with Pool(workers) as pool:
        results = list(tqdm(pool.starmap(import_excel, args), total=len(tbls)-1))
    
    return results


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
    from glass.sql.db   import create_pgdb
    
    # List Tables in DB A
    tbls = lst_tbl(db_a, excludeViews=True, api=typeDBA)
    
    # Create database B
    db_b = create_pgdb(db_b, overwrite=False, api=typeDBB)
    
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
        from glass.prop.shp import get_gtype
        
        gType = get_gtype(df, geomCol=geomCol, gisApi='pandas')
        
        df_to_db(
            db_b, df, tblB, append=True, api='psql', epsg=srsEpsg,
            geom_type=gType, col_geom=geomCol, dbset=con_b
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

    if apidb == 'psql':
        from glass.sql.db import create_pgdb as create_db
    
    else:
        from glass.sql.db import create_sqlitedb as create_db
    
    if not db_exists(db):
        # Create database
        create_db(db, overwrite=None)
    
    else:
        if rewrite:
            create_db(db, overwrite=True)
    
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

def shp_to_psql(dbname, shps, api="pandas", tnames=None,
                map_cols=None, srs=None,
                dbset='default', to_srs=None, fformat=None, lyrname=None,
                mantain_map_cols=None, whr=None, import_all_layers=None):
    """
    Send Shapefile to PostgreSQL
    
    if api == "pandas" - GeoPandas API will be used;
    if api == ogr2ogr - ogr2ogr from GDAL will be used

    shp could be a folder with geofiles
    shp could be a list of geofiles
    shp could be a single geofile

    if shp if a gpkg, layer names will be read from lyrname

    lyrname if a dict like:
    lyrname = {path_to_source: [layer1, layer2], path_to_source: layer_tal}
    """
    
    from glass.cons.psql import con_psql
    from glass.prj.obj   import df_prj
    from glass.prop.prj  import shp_epsg
    from glass.prop.sql  import lst_db
    from glass.pys       import obj_to_lst
    from glass.pys.oss   import lst_ff, fprop
    from glass.rd.shp    import shp_to_obj
    from glass.sql.db    import create_pgdb
    from glass.wt.sql    import df_to_db
    from glass.prop.df   import lst_layers
    
    apis = ["pandas", "ogr2ogr"]

    # If defined, srsEpsgCode must be a integer value
    if srs and type(srs) != int:
        raise ValueError('srs should be a integer value')
    
    if api not in apis:
        raise ValueError(
            f'api value is not valid. options are: {", ".join(apis)}'
        )
    
    # Check if we need to create db or not
    dbs = lst_db()

    if dbname not in dbs:
        create_pgdb(dbname, overwrite=None, use_template=True)
    
    # Check if shp is folder
    if type(shps) == list:
        pass
    else:
        if os.path.isdir(shps) and '.gdb' not in shps:
            shps = lst_ff(shps, file_format=fformat)

    
        else:
            shps = obj_to_lst(shps)
    
    # Relate each file with a layer and epsg
    d = []
    for shp in shps:
        lyrs = [] if not lyrname or shp not in lyrname \
            else obj_to_lst(lyrname[shp])
        
        if not len(lyrs):
            lyr_in_shp = lst_layers(shp)
            lyrs = [lyr_in_shp[0]] if not import_all_layers else \
                lyr_in_shp
        
        for i, l in enumerate(lyrs):
            if not tnames:
                tn = l
            
            else:
                if (shp, l) in tnames:
                    tn = tnames[(shp, l)]
                
                else:
                    if shp in tnames:
                        tn = tnames[shp] if len(lyrs) == 1 else \
                            f'{tnames[shp]}_{str(i)}'
                    
                    else:
                        tn = l
            
            if type(whr) == dict:
                if (shp, l) in whr:
                    _whr = whr[(shp, l)]
                
                else:
                    if shp in whr:
                        _whr = whr[shp]
                    
                    else:
                        _whr = None
            
            elif type(whr) == str:
                _whr = whr
            
            else:
                _whr = None
                
            d.append({
                'src'  : shp,
                'lyr'  : l,
                'epsg' : shp_epsg(shp, lyrname=l) if not srs else srs,
                'tbl'  : tn,
                'whr'  : _whr
            })
    
    # Import data
    tables = []
    for s in d:
        if api == "pandas":
            # SHP to DataFrame
            df = shp_to_obj(s['src'], lyr=s['lyr'])

            # Sanitize columns name
            if not map_cols:
                rname = {x : x.lower() for x in df.columns.values}
                
            else:
                if not mantain_map_cols:
                    rname = {
                        x : map_cols[x].lower() if x in map_cols else \
                        x.lower() for x in df.columns.values
                    }
                
                else:
                    rname= map_cols

                    df.drop(
                        [c for c in df.columns.values if c not in map_cols],
                        axis=1, inplace=True
                    )

            df.rename(columns=rname, inplace=True)
            
            if "geometry" in df.columns.values:
                gcol = "geometry"
            
            elif "geom" in df.columns.values:
                gcol = "geom"
            
            else:
                raise ValueError("No Geometry found in shp")
            
            # Project if necessary
            if to_srs and s['epsg'] != to_srs:
                df = df_prj(df, to_srs)
                tepsg = to_srs
            
            else:
                tepsg = s['epsg']
            
            # GeoDataFrame to PSQL
            df_to_db(
                dbname, df, s['tbl'], append=True, api='psql',
                epsg=tepsg, col_geom=gcol
            )
        
        elif api == 'ogr2ogr':
            con = con_psql()

            lstr = "" if not s["lyr"] else f' {s["lyr"]}'

            ssrs = "" if not to_srs or to_srs == s["epsg"] \
                else f" -s_srs EPSG:{str(s['epsg'])} -t_srs EPSG:{str(to_srs)}"
            
            _whr = "" if not s["whr"] else f' -where "{s["whr"]}"'

            cmd = (
                'ogr2ogr -f "PostgreSQL" "PG:dbname='
                f'\'{dbname}\' host=\'{con["HOST"]}\' port=\'{con["PORT"]}\' '
                f'user=\'{con["USER"]}\' password=\'{con["PASSWORD"]}\'" '
                f'-nln {s["tbl"]} {s["src"]}{lstr}{ssrs}{_whr} -unsetFid '
                f'-lco GEOMETRY_NAME=geom -nlt PROMOTE_TO_MULTI -dim 2'
            )

            ocmd = execmd(cmd)

            rep = os.path.join(os.path.dirname(s["src"]), 'psqlimport.txt')

            with open(rep, 'w') as _rep:
                _rep.write(cmd)
                _rep.write('\n\n\n=======================\n\n\n\n')

                _rep.write(ocmd)
        
        else: continue
        
        tables.append(s['tbl'])
    
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


def osm_to_psql(osmXml, osmdb, dbsetup='default', schema=None):
    """
    Use GDAL to import osmfile into PostGIS database
    """
    
    from glass.cons.psql import con_psql
    from glass.prop.sql  import db_exists
    from glass.sql.q import exec_write_q

    is_db = db_exists(osmdb, dbset=dbsetup)

    if not is_db:
        from glass.sql.db import create_pgdb

        create_pgdb(osmdb, dbset=dbsetup)

    con = con_psql(db_set=dbsetup)

    #_schema  = '' if not schema else f' active_schema={schema}'
    schema_  = '' if not schema else f'-lco SCHEMA={schema} '

    if schema:
        exec_write_q(osmdb, f"CREATE SCHEMA IF NOT EXISTS {schema}")
    
    cmd = (
        f"ogr2ogr -f PostgreSQL \"PG:dbname="
        f"'{osmdb}' host='{con['HOST']}' port='{con['PORT']}' "
        f"user='{con['USER']}' password='{con['PASSWORD']}'\" "
        #f"{_schema}\" "
        f"{osmXml} {schema_}"
        "-lco COLUMN_TYPES=other_tags=hstore"
    )
    
    cmdout = execmd(cmd)
    
    return osmdb



def gpkg_lyr_attr_to_psql(gpkg, lyr, col, db, tbl_bname=None):
    """
    GeoPackage layer to PostgreSQL tables

    For a given layer in a GeoPackage, the values in a given column
    will be listed, for each value, the rows with that value
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

