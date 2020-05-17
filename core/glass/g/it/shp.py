"""
Change File Format
"""

def shp_to_shp(inshp, outshp, gisApi='ogr', supportForSpatialLite=None):
    """
    Convert a vectorial file to another with other file format
    
    API's Available:
    * ogr;
    * grass;
    
    When using gisApi='ogr' - Set supportForSpatialLite to True if outShp is
    a sqlite db and if you want SpatialLite support for that database.
    """
    
    if gisApi == 'ogr':
        from glass.pys    import execmd
        from glass.g.prop import drv_name
        
        out_driver = drv_name(outshp)
    
        if out_driver == 'SQLite' and supportForSpatialLite:
            splite = ' -dsco "SPATIALITE=YES"'
        else:
            splite = ''
    
        cmd = 'ogr2ogr -f "{drv}" {out} {_in}{lite}'.format(
            drv=out_driver, out=outshp, _in=inshp,
            lite=splite
        )
    
        # Run command
        cmdout = execmd(cmd)
    
    elif gisApi == 'grass':
        # TODO identify input geometry type
        
        import os
        from glass.pys.oss    import fprop
        from glass.g.wenv.grs import run_grass
        from glass.g.prop.prj import get_epsg

        # Start GRASS GIS Session
        ws  = os.path.dirname(outshp)
        loc = f'loc_{fprop(outshp, "fn")}'
        epsg = get_epsg(inshp)

        gbase = run_grass(ws, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(gbase, ws, loc, 'PERMANENT')

        from glass.g.it.shp import grs_to_shp, shp_to_grs

        gshp = shp_to_grs(inshp, fprop(inshp, 'fn'))
        grs_to_shp(gshp, outshp, 'area')
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outshp


def foldershp_to_foldershp(inFld, outFld, destiny_file_format,
                           file_format='.shp', useApi='ogr'):
    """
    Execute shp_to_shp for every file in inFld (path to folder)
    
    useApi options:
    * ogr;
    """
    
    import os
    from glass.pys.oss import lst_ff, fprop
    
    if not os.path.exists(outFld):
        from glass.pys.oss import mkdir
        mkdir(outFld)
    
    geo_files = lst_ff(inFld, file_format=file_format)
    
    for f in geo_files:
        shp_to_shp(f, os.path.join(outFld, '{}.{}'.format(
            fprop(f, 'fn'), destiny_file_format if \
                destiny_file_format[0] == '.' else '.' + destiny_file_format
        )), gisApi=useApi)
    
    return outFld


def shps_to_gpkg(in_shps, gpkg, shp_ff='.shp', tbl_name=None):
    """
    Add Shapefile to GeoPackage File
    """

    import os
    from glass.pys      import execmd
    from glass.pys .oss import fprop

    if type(in_shps) == list:
        shps = in_shps
    
    elif os.path.isdir(in_shps):
        from glass.pys .oss import lst_ff

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


def pointXls_to_shp(xlsFile, outShp, x_col, y_col, epsg, sheet=None):
    """
    Excel table with Point information to ESRI Shapefile
    """
    
    from glass.ng.rd    import tbl_to_obj
    from glass.g.it.pd  import pnt_dfwxy_to_geodf
    from glass.g.wt.shp import df_to_shp
    
    # XLS TO PANDAS DATAFRAME
    dataDf = tbl_to_obj(xlsFile, sheet=sheet)
    
    # DATAFRAME TO GEO DATAFRAME
    geoDataDf = pnt_dfwxy_to_geodf(dataDf, x_col, y_col, epsg)
    
    # GEODATAFRAME TO ESRI SHAPEFILE
    df_to_shp(geoDataDf, outShp)
    
    return outShp


"""
GRASS GIS conversions
"""

def shp_to_grs(inLyr, outLyr, filterByReg=None, asCMD=None):
    """
    Add Shape to GRASS GIS
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        f = 'o' if not filterByReg else 'ro'
        
        m = Module(
            "v.in.ogr", input=inLyr, output=outLyr, flags='o',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.in.ogr input={} output={} -o{} --overwrite --quiet"
        ).format(inLyr, outLyr, " -r" if filterByReg else ""))
    
    return outLyr


def grs_to_shp(inLyr, outLyr, geomType, lyrN=1, asCMD=True, asMultiPart=None):
    """
    GRASS Vector to Shape File
    """
    
    from glass.g.prop  import VectorialDrivers
    from glass.pys.oss import fprop
    
    vecDriv = VectorialDrivers()
    outEXT  = fprop(outLyr, 'ff')
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        __flg = None if not asMultiPart else 'm'
        
        m = Module(
            "v.out.ogr", input=inLyr, type=geomType, output=outLyr,
            format=vecDriv[outEXT], flags=__flg, layer=lyrN,
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pys import execmd
        
        rcmd = execmd((
            "v.out.ogr input={} type={} output={} format={} "
            "layer={}{} --overwrite --quiet"  
        ).format(
            inLyr, geomType, outLyr, 
            vecDriv[outEXT], lyrN, " -m" if asMultiPart else ""
        ))
    
    return outLyr


"""
Database Table to Shape
"""

def dbtbl_to_shp(db, tbl, geom_col, outShp, where=None, inDB='psql',
                 notTable=None, filterByReg=None, outShpIsGRASS=None,
                 tableIsQuery=None, api='psql', epsg=None):
    """
    Database Table to Feature Class file
    
    idDB Options:
    * psql
    * sqlite
    
    api Options:
    * psql
    * sqlite
    * pgsql2shp
    
    if outShpIsGRASS if true, the method assumes that outShp is
    a GRASS Vector. That implies that a GRASS Session was been
    started already. 
    """

    from glass.g.wt.shp import df_to_shp
    
    if outShpIsGRASS:
        from glass.pys       import execmd
        from glass.cons.psql import con_psql

        db_con = con_psql()
        
        whr = "" if not where else " where=\"{}\"".format(where)
        
        cmd_str = (
            "v.in.ogr input=\"PG:host={} dbname={} user={} password={} "
            "port={}\" output={} layer={} geometry={}{}{}{} -o --overwrite --quiet"
        ).format(
            db_con["HOST"], db, db_con["USER"], db_con["PASSWORD"],
            db_con["PORT"], outShp, tbl, geom_col, whr,
            " -t" if notTable else "", " -r" if filterByReg else ""
        ) if inDB == 'psql' else (
            "v.in.ogr -o input={} layer={} output={}{}{}{}"
        ).format(db, tbl, outShp, whr,
            " -t" if notTable else "", " -r" if filterByReg else ""
        ) if inDB == 'sqlite' else None
        
        rcmd = execmd(cmd_str)
    
    else:
        if api == 'pgsql2shp':
            from glass.pys  import execmd
            from glass.cons.psql import con_psql

            db_con = con_psql()
            
            outcmd = execmd((
                'pgsql2shp -f {out} -h {hst} -u {usr} -p {pt} -P {pas}{geom} '
                '{bd} {t}'
            ).format(
                hst=db_con['HOST'], usr=db_con["USER"], pt=db_con["PORT"],
                pas=db_con['PASSWORD'], bd=db, out=outShp,
                t=tbl if not tableIsQuery else '"{}"'.format(tbl),
                geom="" if not geom_col else " -g {}".format(geom_col)
            ))
        
        elif api == 'psql' or api == 'sqlite':
            from glass.ng.sql.q import q_to_obj
            
            q = "SELECT * FROM {}".format(tbl) if not tableIsQuery else tbl
            
            df = q_to_obj(db, q, db_api=api, geomCol=geom_col, epsg=epsg)
            
            outsh = df_to_shp(df, outShp)
        
        else:
            raise ValueError((
                'api value must be \'psql\', \'sqlite\' or \'pgsql2shp\''))
    
    return outShp

