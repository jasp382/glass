"""
Data Management Tools > Manage Spatial Reference Systems
"""

import os
from osgeo import osr

from glass.pys import execmd
from glass.prop.df import drv_name
from glass.pys.oss import fprop


def def_prj(shp, epsg=None, api='ogr'):
    """
    Create/Replace the prj file of a ESRI Shapefile

    API options:
    * ogr;
    * epsgio;
    """

    import shutil

    prj_file = os.path.join(
        os.path.dirname(shp),
        f'{fprop(shp, "fn")}.prj'
    )

    if api == 'ogr':
        if epsg and type(epsg) == int:
            s = osr.SpatialReference()
            s.ImportFromEPSG(int(epsg))
            s.MorphToESRI()
            prj = open(prj_file, 'w')
            prj.write(s.ExportToWkt())
            prj.close()
            return prj_file
    
        elif epsg and type(epsg) == str:
            prj_template = f'{fprop(epsg, "fn")}.prj'
        
            if not os.path.exists(prj_template):
                return 0
        
            try:
                os.remove(prj_file)
                shutil.copyfile(prj_template, prj_file)
            except:
                shutil.copyfile(prj_template, prj_file)
    
    elif api == 'epsg.io':
        if not epsg:
            raise ValueError((
                "TO use epsgio option, epsg parameter must be given"
            ))
        
        from glass.pys.web import get_file
        from glass.pys.oss import del_file

        url = f'https://epsg.io/{str(epsg)}.wkt?download'

        if os.path.exists(prj_file):
            # Delete file
            del_file(prj_file)
        
        # Get new prj
        get_file(url, prj_file)
        
    return prj_file


def proj(inShp, outShp, outEPSG, inEPSG=None,
        api='ogr', sql=None, db_name=None, ilyr=None, olyr=None):
    """
    Project Geodata using GIS
    
    API's Available:
    * ogr;
    * ogr2ogr;
    * pandas;
    * ogr2ogr_SQLITE;
    * psql;
    """
    
    if api == 'ogr':
        """
        Using ogr Python API
        """
        
        from osgeo           import ogr
        from glass.lyr.fld   import copy_flds
        from glass.prop.feat import get_gtype
        from glass.prop.prj  import sref_from_epsg, trans_param, shp_sref
        
        def copyShp(out, outDefn, lyr_in, trans):
            for f in lyr_in:
                g = f.GetGeometryRef()
                g.Transform(trans)
                new = ogr.Feature(outDefn)
                new.SetGeometry(g)
                for i in range(0, outDefn.GetFieldCount()):
                    new.SetField(outDefn.GetFieldDefn(i).GetNameRef(), f.GetField(i))
                out.CreateFeature(new)
                new.Destroy()
                f.Destroy()
        
        # ####### #
        # Project #
        # ####### #
        inData = ogr.GetDriverByName(
            drv_name(inShp)).Open(inShp, 0)
        
        inLyr = inData.GetLayer()

        in_epsg = inEPSG if inEPSG else shp_sref(inLyr)

        transP = trans_param(in_epsg, outEPSG)

        out = ogr.GetDriverByName(
            drv_name(outShp)).CreateDataSource(outShp)
        
        outlyr = out.CreateLayer(
            fprop(outShp, 'fn'), sref_from_epsg(outEPSG),
            geom_type=get_gtype(
                inShp, name=None, py_cls=True, gisApi='ogr'
            )
        )
        
        # Copy fields to the output
        copy_flds(inLyr, outlyr)
        # Copy/transform features from the input to the output
        outlyrDefn = outlyr.GetLayerDefn()
        copyShp(outlyr, outlyrDefn, inLyr, transP)
        
        inData.Destroy()
        out.Destroy()
    
    elif api == 'ogr2ogr':
        """
        Transform SRS of any OGR Compilant Data. Save the transformed data
        in a new file
        """

        if not inEPSG:
            from glass.prop.prj import shp_epsg
            inEPSG = shp_epsg(inShp)
        
        if not inEPSG:
            raise ValueError('To use ogr2ogr, you must specify inEPSG')

        drv = drv_name(outShp)

        up = "" if drv != 'GPKG' else f" -update -append" \
            if os.path.exists(outShp) else ""
        
        otbl = olyr if olyr else fprop(outShp, 'fn')

        if not sql and not ilyr:
            _sql = ''
        elif not sql and ilyr:
            _sql = f' -dialect sqlite -sql "SELECT * FROM {ilyr}"'
        else:
            _sql = f' -dialect sqlite -sql "{sql}"'
        
        ocmd = execmd((
            f'ogr2ogr{up} -f "{drv}" {outShp} -nln "{otbl}" '
            f'{inShp}{_sql} '
            f'-s_srs EPSG:{str(inEPSG)} '
            f'-t_srs EPSG:{str(outEPSG)}'
        ))
    
    elif api == 'ogr2ogr_SQLITE':
        """
        Transform SRS of a SQLITE DB table. Save the transformed data in a
        new table
        """
        
        if not inEPSG:
            raise ValueError((
                'With ogr2ogr_SQLITE, the definition of inEPSG is '
                'demandatory.'
            ))
        
        # TODO: Verify if database is sqlite
        
        db, tbl = inShp['DB'], inShp['TABLE']
        sql = f'SELECT * FROM {tbl}' if not sql else sql
        
        outcmd = execmd((
            f'ogr2ogr -update -append -f "SQLite" {db} -nln "{outShp}" '
            f'-dialect sqlite -sql "{_sql}" -s_srs EPSG:{str(inEPSG)} '
            f'-t_srs EPSG:{str(outEPSG)} {db}'
        ))
    
    elif api == 'pandas':
        # Test if input Shp is GeoDataframe
        from glass.rd.shp import shp_to_obj
        from glass.wt.shp import df_to_shp

        df = shp_to_obj(inShp)
        
        # Project df
        newDf = df.to_crs(f'EPSG:{outEPSG}')
        
        # Save as file 
        return df_to_shp(df, outShp)
    
    elif api == 'psql':
        from glass.sql.db  import create_pgdb
        from glass.it.db   import shp_to_psql
        from glass.it.shp  import dbtbl_to_shp
        from glass.prj.sql import sql_proj

        # Create Database
        if not db_name:
            db_name = create_pgdb(fprop(
                outShp, 'fn', forceLower=True)
            )
        
        else:
            from glass.prop.sql import db_exists

            isDb = db_exists(db_name)

            if not isDb:
                create_pgdb(db_name)

        # Import Data
        inTbl = shp_to_psql(db_name, inShp, api='shp2pgsql', encoding="LATIN1")

        # Transform
        oTbl = sql_proj(
            db_name, inTbl, fprop(outShp, 'fn', forceLower=True),
            outEPSG, geomCol='geom', newGeom='geom'
        )

        # Export
        outShp = dbtbl_to_shp(
            db_name, oTbl, 'geom', outShp, api='psql', epsg=outEPSG
        )
    
    else:
        raise ValueError(f'Sorry, API {api} is not available')
    
    return outShp


"""
Manage spatial reference systems of any raster dataset
"""

def set_proj(rst, epsg):
    """
    Define Raster projection
    """
    
    from osgeo import gdal
    
    img = gdal.Open(rst, 1)
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    
    img.SetProjection(srs.ExportToWkt())
    
    img.FlushCache()


def reprj_rst(inRst, outRst, inEPSG, outEPSG):
    """
    Reproject Raster dataset using gdalwarp
    """
    
    ocmd = execmd((
        f'gdalwarp -overwrite {inRst} {outRst} '
        f'-s_srs EPSG:{inEPSG} '
        f'-t_srs EPSG:{outEPSG}'
    ))
    
    return outRst

