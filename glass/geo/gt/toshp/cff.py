"""
Change File Format
"""

def shp_to_shp(inShp, outShp, gisApi='ogr', supportForSpatialLite=None):
    """
    Convert a vectorial file to another with other file format
    
    API's Available:
    * ogr;
    
    When using gisApi='ogr' - Set supportForSpatialLite to True if outShp is
    a sqlite db and if you want SpatialLite support for that database.
    """
    
    import os
    
    if gisApi == 'ogr':
        from glass.pyt            import execmd
        from glass.geo.gt.prop.ff import drv_name
        
        out_driver = drv_name(outShp)
    
        if out_driver == 'SQLite' and supportForSpatialLite:
            splite = ' -dsco "SPATIALITE=YES"'
        else:
            splite = ''
    
        cmd = 'ogr2ogr -f "{drv}" {out} {_in}{lite}'.format(
            drv=out_driver, out=outShp, _in=inShp,
            lite=splite
        )
    
        # Run command
        cmdout = execmd(cmd)
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp


def foldershp_to_foldershp(inFld, outFld, destiny_file_format,
                           file_format='.shp', useApi='ogr'):
    """
    Execute shp_to_shp for every file in inFld (path to folder)
    
    useApi options:
    * ogr;
    """
    
    import os
    from glass.pyt.oss import lst_ff, fprop
    
    if not os.path.exists(outFld):
        from glass.pyt.oss import mkdir
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
    from glass.pyt     import execmd
    from glass.pyt.oss import fprop

    if type(in_shps) == list:
        shps = in_shps
    
    elif os.path.isdir(in_shps):
        from glass.pyt.oss import lst_ff

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
        from glass.pyt import execmd
        
        rcmd = execmd((
            "v.in.ogr input={} output={} -o{} --overwrite --quiet"
        ).format(inLyr, outLyr, " -r" if filterByReg else ""))
    
    return outLyr


def grs_to_shp(inLyr, outLyr, geomType, lyrN=1, asCMD=True, asMultiPart=None):
    """
    GRASS Vector to Shape File
    """
    
    from glass.geo.gt.prop.ff import VectorialDrivers
    from glass.pyt.oss    import fprop
    
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
        from glass.pyt import execmd
        
        rcmd = execmd((
            "v.out.ogr input={} type={} output={} format={} "
            "layer={}{} --overwrite --quiet"  
        ).format(
            inLyr, geomType, outLyr, 
            vecDriv[outEXT], lyrN, " -m" if asMultiPart else ""
        ))
    
    return outLyr
