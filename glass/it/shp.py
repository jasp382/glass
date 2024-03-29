"""
Change File Format
"""

import os

from glass.pys import execmd

def shp_to_shp(inshp, outshp, gapi='ogr', spatialite=None, lyrname=None):
    """
    Convert a vectorial file to another with other file format
    
    API's Available:
    * ogr;
    * grass;
    
    When using gapi='ogr' - Set supportForSpatialLite to True if outShp is
    a sqlite db and if you want SpatialLite support for that database.
    """
    
    if gapi == 'ogr':
        from glass.prop.df import drv_name
        
        drv = drv_name(outshp)
    
        if drv == 'SQLite' and spatialite:
            splite = ' -dsco "SPATIALITE=YES"'
        else:
            splite = ''

        lstr = "" if not lyrname else f' {lyrname}'
    
        cmd = f'ogr2ogr -f "{drv}" {outshp} {inshp}{lstr}{splite}'
    
        # Run command
        cmdout = execmd(cmd)
    
    elif gapi == 'grass':
        # TODO identify input geometry type
        
        from glass.pys.oss  import fprop
        from glass.wenv.grs import run_grass
        from glass.prop.prj import get_epsg

        # Start GRASS GIS Session
        ws  = os.path.dirname(outshp)
        loc = f'loc_{fprop(outshp, "fn")}'
        epsg = get_epsg(inshp)

        gbase = run_grass(ws, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(gbase, ws, loc, 'PERMANENT')

        from glass.it.shp import grs_to_shp, shp_to_grs

        gshp = shp_to_grs(inshp, fprop(inshp, 'fn'))
        grs_to_shp(gshp, outshp, 'area')
    
    else:
        raise ValueError(f'Sorry, API {gapi} is not available')
    
    return outshp


def foldershp_to_foldershp(inFld, outFld, destiny_file_format,
                           file_format='.shp', useApi='ogr'):
    """
    Execute shp_to_shp for every file in inFld (path to folder)
    
    useApi options:
    * ogr;
    """
    
    from glass.pys.oss import lst_ff, fprop
    
    if not os.path.exists(outFld):
        from glass.pys.oss import mkdir
        mkdir(outFld)
    
    geo_files = lst_ff(inFld, file_format=file_format)
    
    for f in geo_files:
        name = fprop(f, 'fn')

        ff = destiny_file_format if \
            destiny_file_format[0] == '.' else '.' + destiny_file_format
        
        shp_to_shp(f, os.path.join(outFld, f'{name}.{ff}'), gapi=useApi)
    
    return outFld


def pointXls_to_shp(xlsFile, outShp, x_col, y_col, epsg, sheet=None):
    """
    Excel table with Point information to ESRI Shapefile
    """
    
    from glass.rd     import tbl_to_obj
    from glass.it.pd  import pnt_dfwxy_to_geodf
    from glass.wt.shp import df_to_shp
    
    # XLS TO PANDAS DATAFRAME
    dataDf = tbl_to_obj(xlsFile, sheet=sheet)
    
    # DATAFRAME TO GEO DATAFRAME
    geoDataDf = pnt_dfwxy_to_geodf(dataDf, x_col, y_col, epsg)
    
    # GEODATAFRAME TO ESRI SHAPEFILE
    df_to_shp(geoDataDf, outShp)
    
    return outShp


def tblpnt_to_shp(tbl, shp, xcol, ycol, epsg, outepsg=None, 
    sheet=None, delimiter='\t', noheaders=None, noheaderscols=None):
    """
    Regular table with points to Feature Class
    """

    from glass.rd      import tbl_to_obj
    from glass.it.pd   import pnt_dfwxy_to_geodf
    from glass.prj.obj import df_prj
    from glass.wt.shp  import df_to_shp

    df = tbl_to_obj(
        tbl, _delimiter=delimiter,
        csvheader=True if not noheaders else None,
        sheet=sheet
    )

    if noheaders and noheaderscols:
        ncols = len(list(df.columns.values))
        cols_name = {
            i : noheaderscols[i] for i in range(ncols)
        }

        df.rename(columns=cols_name, inplace=True)
    
    df = pnt_dfwxy_to_geodf(df, xcol, ycol, epsg)

    if outepsg and epsg != outepsg:
        df = df_prj(df, outepsg)

        epsg = outepsg

    df_to_shp(df, shp)

    return shp


"""
GRASS GIS conversions
"""

def shp_to_grs(ilyr: str, olyr:str|None=None,
               filterByReg: bool|None=None,
               lyrname: str|None=None,
               asCMD: bool|None=None):
    """
    Add Shape to GRASS GIS
    """

    from glass.pys.oss import fprop

    if not olyr:
        olyr = lyrname if lyrname else fprop(ilyr, 'fn', forceLower=True)
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        f = 'o' if not filterByReg else 'ro'
        
        m = Module(
            "v.in.ogr", input=ilyr, layer=lyrname,
            output=olyr, flags=f,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd

        f = " -r" if filterByReg else ""
        lyr = '' if not lyrname else f" layer={lyrname}"
        
        rcmd = execmd((
            f"v.in.ogr input={ilyr}{lyr} "
            f"output={olyr} -o{f} --overwrite --quiet"
        ))
    
    return olyr


def grs_to_shp(ilyr, olyr, geomtype, lyrn=1,
               ascmd=True, asMultiPart=None, lname=None):
    """
    GRASS Vector to Shape File
    """
    
    from glass.prop.df import grs_shp_drv
    from glass.pys.oss import fprop
    
    vecDriv = grs_shp_drv()
    outEXT  = fprop(olyr, 'ff')
    geoff   = vecDriv[outEXT]

    _update = True if geoff == 'GPKG' and \
        os.path.exists(olyr) else None
    
    if not ascmd:
        from grass.pygrass.modules import Module
        
        __flg = None if not asMultiPart and not _update else (
            f'{"m" if asMultiPart else ""}'
            f'{"u" if _update else ""}'
        )
        
        m = Module(
            "v.out.ogr", input=ilyr, type=geomtype, output=olyr,
            format=geoff, flags=__flg, layer=lyrn,
            output_layer=lname,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        mp    = " -m" if asMultiPart else ""
        up    = " -u" if _update else ""
        olyrn = '' if not lname else f"output_layer={lname}"
 
        rcmd = execmd((
            f"v.out.ogr input={ilyr} type={geomtype} "
            f"output={olyr} format={geoff} "
            f"layer={lyrn}{olyrn}{mp}{up} "
            "--overwrite --quiet"  
        ))
    
    return olyr


"""
Database Table to Shape
"""

def dbtbl_to_shp(db, tbl, geom_col, outShp, where=None, inDB='psql',
                 notTable=None, filterByReg=None,
                 tableIsQuery=None, api='psql', epsg=None, dbset='default',
                 olyr=None):
    """
    Database Table to Feature Class file
    
    idDB Options:
    * psql
    * sqlite
    
    api Options:
    * psql
    * sqlite
    * pgsql2shp
    * grass
    * ogr2ogr
    
    if outShpIsGRASS if true, the method assumes that outShp is
    a GRASS Vector. That implies that a GRASS Session was been
    started already. 
    """

    from glass.wt.shp    import df_to_shp
    from glass.pys       import execmd
    from glass.cons.psql import con_psql
    
    if api == 'grass':
        db_con = con_psql(db_set=dbset)
        
        whr = "" if not where else f" where=\"{where}\""
        t = " -t" if notTable else ""
        r = " -r" if filterByReg else ""

        cmd_str = (
            f"v.in.ogr input=\"PG:host={db_con['HOST']} "
            f"dbname={db} user={db_con['USER']} "
            f"password={db_con['PASSWORD']} "
            f"port={db_con['PORT']}\" output={outShp} "
            f"layer={tbl} geometry={geom_col}"
            f"{whr}{t}{r} -o --overwrite --quiet"
        ) if inDB == 'psql' else (
            f"v.in.ogr -o input={db} "
            f"layer={tbl} output={outShp}"
            f"{whr}{' -t' if notTable else ''}"
            f"{' -r' if filterByReg else ''}"
        ) if inDB == 'sqlite' else None
        
        rcmd = execmd(cmd_str)
    
    elif api == 'pgsql2shp':
        db_con = con_psql(db_set=dbset)
            
        geom = '' if not geom_col else f' -g {geom_col}'
        t    = tbl if not tableIsQuery else f'"{tbl}"'
            
        outcmd = execmd((
            f"pgsql2shp -f {outShp} -h {db_con['HOST']} "
            f"-u {db_con['USER']} -p {db_con['PORT']} "
            f"-P {db_con['PASSWORD']} -k"
            f"{geom} {db} {t}"
        ))
        
    elif api == 'psql' or api == 'sqlite':
        from glass.sql.q import q_to_obj
            
        q = f"SELECT * FROM {tbl}" if not tableIsQuery else tbl
            
        df = q_to_obj(
            db, q, db_api=api, geomCol=geom_col, epsg=epsg,
            dbset=dbset
        )
            
        outsh = df_to_shp(df, outShp)
    
    elif api == 'ogr2ogr':
        from glass.prop.df import drv_name
        from glass.pys.oss import fprop

        cdb = con_psql(db_set=dbset)

        drv = drv_name(outShp)

        up = "" if drv != 'GPKG' else f" -update -append" \
            if os.path.exists(outShp) else ""
        
        otbl = olyr if olyr else fprop(outShp, 'fn')

        qtbl = f"\"{tbl}\"" if not tableIsQuery else f"-sql \"{tbl}\""
        
        cmd = (
            f"ogr2ogr{up} -f \"{drv}\" {outShp} -nln \"{otbl}\" "
            f"PG:\"dbname='{db}' host='{cdb['HOST']}' port='{cdb['PORT']}' "
            f"user='{cdb['USER']}' password='{cdb['PASSWORD']}'\" "
            f"{qtbl}"
        )

        ocmd = execmd(cmd)
        
    else:
        raise ValueError((
            'api value must be \'psql\', \'sqlite\' or \'pgsql2shp\''))
    
    return outShp


"""
Something to GeoPackage
"""


def shps_to_gpkg(in_shps, gpkg, shp_ff='.shp', tbl_name=None):
    """
    Add Shapefile to GeoPackage File
    """

    from glass.pys.oss import fprop

    if type(in_shps) == list:
        shps = in_shps
    
    elif os.path.isdir(in_shps):
        from glass.pys.oss import lst_ff

        # List Feature Classes
        shps = lst_ff(in_shps, file_format='.shp' if not shp_ff else shp_ff)
    
    else:
        # Assuming in_shps as a file
        shps = [in_shps]
    
    new_cmd = "ogr2ogr -f \"GPKG\" {} -nln \"{}\" {}"
    upd_cmd = "ogr2ogr -update -append -f \"GPKG\" {} -nln \"{}\" {}"

    for s in range(len(shps)):
        if tbl_name and not s:
            tname = tbl_name
        else:
            tname = fprop(shps[s], 'fn')
        
        if not s and not os.path.exists(gpkg):
            rcmd = execmd(new_cmd.format(gpkg, tname, shps[s]))
        else:
            rcmd = execmd(upd_cmd.format(gpkg, tname, shps[s]))

    return gpkg


def db_to_gpkg(db, itbl, gpkg, otbl=None):
    """
    Database table to GeoPackage
    """

    from glass.cons.psql import con_psql

    cdb = con_psql()

    otbl = itbl if not otbl else otbl

    up = " -update -append" if os.path.exists(gpkg) \
        else ""

    cmd = (
        f"ogr2ogr{up} -f \"GPKG\" {gpkg} -nln \"{otbl}\" "
        f"PG:\"dbname='{db}' host='{cdb['HOST']}' port='{cdb['PORT']}' "
        f"user='{cdb['USER']}' password='{cdb['PASSWORD']}'\" "
        f"\"{itbl}\""
    )

    ocmd = execmd(cmd)

    return gpkg


def gdb_to_gpkg(gdb, layers, gpkg):
    """
    GeoDatabase Feature Classes to a new GeoPackage
    """

    from glass.pys import obj_to_lst

    lyrs = obj_to_lst(layers)

    for i in range(len(lyrs)):
        up = " -update -append" if i else ""

        cmd = (
            f"ogr2ogr{up} -f \"GPKG\" {gpkg} -nln \"{lyrs[i]}\" "
            f"{gdb} -dialect sqlite -sql \"SELECT * FROM {lyrs[i]}\""
        )

        rcmd = execmd(cmd)

    return gpkg

