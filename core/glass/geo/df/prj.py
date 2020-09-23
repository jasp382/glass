# -*- coding: utf-8 -*-

"""
Data Management Tools > Manage Spatial Reference Systems
"""

from osgeo import osr

def def_prj(shp, epsg=None, template=None, api='ogr'):
    """
    Create/Replace the prj file of a ESRI Shapefile

    API options:
    * ogr;
    * epsgio;
    """
    
    import os
    import shutil

    prj_file = os.path.join(os.path.dirname(shp), '{}.prj'.format(
        os.path.splitext(os.path.basename(shp))[0]
    ))

    if api == 'ogr':
        if epsg and not template:
            s = osr.SpatialReference()
            s.ImportFromEPSG(int(epsg))
            s.MorphToESRI()
            prj = open(prj_file, 'w')
            prj.write(s.ExportToWkt())
            prj.close()
            return prj_file
    
        elif not epsg and template:
            prj_template = '{}.prj'.format(
                os.path.splitext(os.path.basename(template))[0]
            )
        
            if not os.path.exists(prj_template):
                return 0
        
            try:
                os.remove(prj_file)
                shutil.copyfile(prj_template, prj_file)
            except:
                shutil.copyfile(prj_template, prj_file)
    
    elif api == 'epsgio':
        if not epsg:
            raise ValueError((
                "TO use epsgio option, epsg parameter must be given"
            ))
        
        from glass.pys.web import get_file
        from glass.pys.oss import del_file

        url = 'https://epsg.io/{}.wkt?download'

        if os.path.exists(prj_file):
            # Delete file
            del_file(prj_file)
        
        # Get new prj
        get_file(url.format(str(epsg)), prj_file)
        
    return prj_file


def proj(inShp, outShp, outEPSG, inEPSG=None,
        gisApi='ogr', sql=None, db_name=None):
    """
    Project Geodata using GIS
    
    API's Available:
    * ogr;
    * ogr2ogr;
    * pandas;
    * ogr2ogr_SQLITE;
    * psql;
    """
    import os
    
    if gisApi == 'ogr':
        """
        Using ogr Python API
        """
        
        if not inEPSG:
            raise ValueError(
                'To use ogr API, you should specify the EPSG Code of the'
                ' input data using inEPSG parameter'
            )
        
        from osgeo                  import ogr
        from glass.geo.obj.lyr.fld   import copy_flds
        from glass.geo.prop.feat import get_gtype
        from glass.geo.prop.df   import drv_name
        from glass.geo.prop.prj  import get_sref_from_epsg, get_trans_param
        from glass.pys.oss          import fprop
        
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
        transP = get_trans_param(inEPSG, outEPSG)
        
        inData = ogr.GetDriverByName(
            drv_name(inShp)).Open(inShp, 0)
        
        inLyr = inData.GetLayer()
        out = ogr.GetDriverByName(
            drv_name(outShp)).CreateDataSource(outShp)
        
        outlyr = out.CreateLayer(
            fprop(outShp, 'fn'), get_sref_from_epsg(outEPSG),
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
    
    elif gisApi == 'ogr2ogr':
        """
        Transform SRS of any OGR Compilant Data. Save the transformed data
        in a new file
        """

        if not inEPSG:
            from glass.geo.prop.prj import get_epsg_shp
            inEPSG = get_epsg_shp(inShp)
        
        if not inEPSG:
            raise ValueError('To use ogr2ogr, you must specify inEPSG')
        
        from glass.pys            import execmd
        from glass.geo.prop.df import drv_name
        
        cmd = (
            'ogr2ogr -f "{}" {} {}{} -s_srs EPSG:{} -t_srs EPSG:{}'
        ).format(
            drv_name(outShp), outShp, inShp,
            '' if not sql else ' -dialect sqlite -sql "{}"'.format(sql),
            str(inEPSG), str(outEPSG)
        )
        
        outcmd = execmd(cmd)
    
    elif gisApi == 'ogr2ogr_SQLITE':
        """
        Transform SRS of a SQLITE DB table. Save the transformed data in a
        new table
        """
        
        from glass.pys import execmd
        
        if not inEPSG:
            raise ValueError((
                'With ogr2ogr_SQLITE, the definition of inEPSG is '
                'demandatory.'
            ))
        
        # TODO: Verify if database is sqlite
        
        db, tbl = inShp['DB'], inShp['TABLE']
        sql = 'SELECT * FROM {}'.format(tbl) if not sql else sql
        
        outcmd = execmd((
            'ogr2ogr -update -append -f "SQLite" {db} -nln "{nt}" '
            '-dialect sqlite -sql "{_sql}" -s_srs EPSG:{inepsg} '
            '-t_srs EPSG:{outepsg} {db}'
        ).format(
            db=db, nt=outShp, _sql=sql, inepsg=str(inEPSG),
            outepsg=str(outEPSG)
        ))
    
    elif gisApi == 'pandas':
        # Test if input Shp is GeoDataframe
        from glass.dct.geo.fmshp import shp_to_obj
        from glass.dct.geo.toshp import df_to_shp

        df = shp_to_obj(inShp)
        
        # Project df
        newDf = df.to_crs('EPSG:{}'.format(str(outEPSG)))
        
        # Save as file 
            
        return df_to_shp(df, outShp)
    
    elif gisApi == 'psql':
        from glass.sql.db           import create_db
        from glass.pys.oss          import fprop
        from glass.dct.gql          import shp_to_psql
        from glass.dct.geo.toshp.db import dbtbl_to_shp
        from glass.geo.gql.prj      import sql_proj

        # Create Database
        if not db_name:
            db_name = create_db(fprop(
                outShp, 'fn', forceLower=True), api='psql'
            )
        
        else:
            from glass.sql.prop import db_exists

            isDb = db_exists(db_name)

            if not isDb:
                create_db(db_name, api='psql')

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
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp


"""
Manage spatial reference systems of any raster dataset
"""

def set_proj(rst, epsg):
    """
    Define Raster projection
    """
    
    from osgeo import osr
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
    
    import sys
    from glass.pys import execmd
    
    cmd = (
        'gdalwarp -overwrite {inrst} {outrst} -s_srs EPSG:{inepsg} '
        '-t_srs EPSG:{outepsg}'
    ).format(
        inrst=inRst, inepsg=inEPSG,
        outrst=outRst, outepsg=outEPSG
    )
    
    codecmd = execmd(cmd)
    
    return outRst

