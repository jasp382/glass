"""
Multi-Files to Single File
"""

import os


def vpatch(shps, outshp):
    """
    GRASS GIS tool to merge shapes
    """

    from glass.pys import execmd

    rcmd = execmd((
        f"v.patch input={','.join(shps)} output={outshp} "
        "--overwrite --quiet"
    ))
    
    return outshp


def shps_to_shp(shps, outShp, api="ogr2ogr", fformat='.shp',
    dbname=None):
    """
    Get all features in several Shapefiles and save them in one file

    api options:
    * ogr2ogr;
    * psql;
    * pandas;
    * psql;
    * grass;
    """

    if type(shps) != list:
        # Check if is dir
        if os.path.isdir(shps):
            from glass.pys.oss import lst_ff
            # List shps in dir
            shps = lst_ff(shps, file_format=fformat)
        
        else:
            raise ValueError((
                'shps should be a list with paths for Feature Classes or a path to '
                'folder with Feature Classes'
            ))

    
    if api == "ogr2ogr":
        from glass.pys  import execmd
        from glass.prop import drv_name
        
        out_drv = drv_name(outShp)
        
        # Create output and copy some features of one layer (first in shps)
        cmdout = execmd(f'ogr2ogr -f "{out_drv}" {outShp} {shps[0]}')
        
        # Append remaining layers
        lcmd = [execmd(
            f'ogr2ogr -f "{out_drv}" -update -append {outShp} {shps[i]}'
        ) for i in range(1, len(shps))]
    
    elif api == 'pandas':
        """
        Merge SHP using pandas
        """
        
        import pandas as pd
        from glass.rd.shp import shp_to_obj
        from glass.wt.shp import df_to_shp
        
        if type(shps) != list:
            raise ValueError('shps should be a list with paths for Feature Classes')
        
        dfs = [shp_to_obj(shp) for shp in shps]

        result = pd.concat(dfs, ignore_index=True)
        
        df_to_shp(result, outShp)
    
    elif api == 'psql':
        from glass.sql.tbl import tbls_to_tbl, del_tables
        from glass.it.db   import shp_to_psql

        if not dbname:
            from glass.sql.db import create_db

            create_db(dbname, api='psql')

        pg_tbls = shp_to_psql(
            dbname, shps, api="shp2pgsql"
        )

        if os.path.isfile(outShp):
            from glass.pys.oss import fprop
            outbl = fprop(outShp, 'fn')
        
        else:
            outbl = outShp

        tbls_to_tbl(dbname, pg_tbls, outbl)

        if outbl != outShp:
            from glass.it.shp import dbtbl_to_shp

            dbtbl_to_shp(
                dbname, outbl, 'geom', outShp, inDB='psql',
                api="pgsql2shp"
            )

        del_tables(dbname, pg_tbls)
    
    elif api == 'grass':
        from glass.wenv.grs import run_grass
        from glass.pys.oss  import fprop, lst_ff
        from glass.prop.prj import get_shp_epsg

        lshps = lst_ff(shps, file_format='.shp')
        
        epsg = get_shp_epsg(lshps[0])

        gwork = os.path.dirname(outShp)
        outshpname = fprop(outShp, "fn")
        loc   = f'loc_{outshpname}'
        gbase = run_grass(gwork, loc=loc, srs=epsg)

        import grass.script.setup as gsetup
        gsetup.init(gbase, gwork, loc, 'PERMANENT')

        from glass.it.shp import shp_to_grs, grs_to_shp

        # Import data
        gshps = [shp_to_grs(s, asCMD=True) for s in lshps]

        patch = vpatch(gshps, outshpname)

        grs_to_shp(patch, outShp, "area")
       
    else:
        raise ValueError(f"{api} API is not available")
    
    return outShp


def same_attr_to_shp(inShps, interestCol, outFolder, basename="data_",
                     resultDict=None):
    """
    For several SHPS with the same field, this program will list
    all values in such field and will create a new shp for all
    values with the respective geometry regardeless the origin shp.
    """
    
    from glass.rd.shp     import shp_to_obj
    from glass.dtr.mge.pd import merge_df
    from glass.wt.shp     import df_to_shp
    
    EXT = os.path.splitext(inShps[0])[1]
    
    shpDfs = [shp_to_obj(shp) for shp in inShps]
    
    DF = merge_df(shpDfs, ignIndex=True)
    #DF.dropna(axis=0, how='any', inplace=True)
    
    uniqueVal = DF[interestCol].unique()
    
    nShps = [] if not resultDict else {}
    for val in uniqueVal:
        ndf = DF[DF[interestCol] == val]
        
        KEY = str(val).split('.')[0] if '.' in str(val) else str(val)
        
        nshp = df_to_shp(ndf, os.path.join(
            outFolder, f'{basename}{KEY}{EXT}'
        ))
        
        if not resultDict:
            nShps.append(nshp)
        else:
            nShps[KEY] = nshp
    
    return nShps


def merge_sameshp_in_diffld(folder, fname, oshp):
    """
    Merge same file in different folders

    Imagine you have several folders, inside of each one of them there
    is a file with a certain name. This will program will create a new file
    with all data in the files with the same name in each folder.
    """

    from glass.pys.oss import lst_fld

    shps = [os.path.join(f, fname) for f in lst_fld(folder)]

    _ = shps_to_shp(shps, oshp, api='pandas')

    return oshp

