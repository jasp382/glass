"""
Any type of data to raster
"""

"""
Feature Class to Raster
"""

def grsshp_to_grsrst(inshp, src, outrst, cmd=None):
    """
    GRASS Vector to GRASS Raster

    api:
    * pygrass
    * grass

    Vectorial geometry to raster
    
    If source is None, the convertion will be based on the cat field.
    
    If source is a string, the convertion will be based on the field
    with a name equal to the given string.
    
    If source is a numeric value, all cells of the output raster will have
    that same value.
    """

    __USE = "cat" if not src else "attr" if type(src) == str \
        else "val" if type(src) == int or \
        type(src) == float else None
    
    if not __USE:
        raise ValueError('\'source\' parameter value is not valid')
    
    if not cmd:
        from grass.pygrass.modules import Module
            
        m = Module(
            "v.to.rast", input=inshp, output=outrst, use=__USE,
            attribute_column=src if __USE == "attr" else None,
            value=src if __USE == "val" else None,
            overwrite=True, run_=False, quiet=True
        )
            
        m()
    
    else:
        from glass.pys import execmd
            
        rcmd = execmd((
            "v.to.rast input={} output={} use={}{} "
            "--overwrite --quiet"
        ).format(
            inshp, outrst, __USE,
            "" if __USE == "cat" else f" attribute_column={src}" \
                if __USE == "attr" else f" val={src}"
        ))

    return outrst


def shp_to_rst(shp, inSource, cellsize, nodata, outRaster, epsg=None,
               rst_template=None, snapRst=None, api='gdal'):
    """
    Feature Class to Raster
    
    cellsize will be ignored if rst_template is defined
    
    * API's Available:
    - gdal;
    - pygrass;
    - grass;
    """
    
    if api == 'gdal':
        from osgeo        import gdal, ogr
        from glass.prop import drv_name
    
        if not epsg:
            from glass.prop.prj import get_shp_sref

            srs = get_shp_sref(shp).ExportToWkt()
        else:
            from glass.prop.prj import epsg_to_wkt
            srs = epsg_to_wkt(epsg)
    
        # Get Extent
        dtShp = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0)
    
        lyr = dtShp.GetLayer()
    
        if not rst_template:
            if not snapRst:
                x_min, x_max, y_min, y_max = lyr.GetExtent()
                x_res = int((x_max - x_min) / cellsize)
                y_res = int((y_max - y_min) / cellsize)
            
            else:
                from glass.prop.rst import adjust_ext_to_snap
                
                x_min, y_max, y_res, x_res, cellsize = adjust_ext_to_snap(
                    shp, snapRst
                )
    
        else:
            from glass.rd.rst import rst_to_array
        
            img_temp = gdal.Open(rst_template)
            geo_transform = img_temp.GetGeoTransform()
        
            y_res, x_res = rst_to_array(rst_template).shape
    
        # Create output
        dtRst = gdal.GetDriverByName(drv_name(outRaster)).Create(
            outRaster, x_res, y_res, gdal.GDT_Byte
        )
    
        if not rst_template:
            dtRst.SetGeoTransform((x_min, cellsize, 0, y_max, 0, -cellsize))
    
        else:
            dtRst.SetGeoTransform(geo_transform)
        
        dtRst.SetProjection(str(srs))
    
        bnd = dtRst.GetRasterBand(1)
        bnd.SetNoDataValue(nodata)
    
        gdal.RasterizeLayer(dtRst, [1], lyr, burn_values=[1])
    
        del lyr
        dtShp.Destroy()
    
    elif api == 'grass' or api == 'pygrass':
        """
        Use GRASS GIS
        - Start Session
        - Import data
        - Convert
        - Export
        """
        
        import os
        from glass.pys.oss    import fprop
        from glass.wenv.grs import run_grass
        from glass.prop.prj import get_epsg

        # Create GRASS GIS Session
        ws = os.path.dirname(outRaster)
        loc = fprop(outRaster, 'fn')
        epsg = get_epsg(shp)

        gbase = run_grass(ws, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(gbase, ws, loc, 'PERMANENT')

        # Import Packages
        from glass.it.shp   import shp_to_grs
        from glass.it.rst   import grs_to_rst
        from glass.wenv.grs import shp_to_region

        # Shape to GRASS GIS
        gshp = shp_to_grs(shp, fprop(shp, 'fn'), asCMD=True)

        # Set Region
        shp_to_region(gshp, cellsize)

        # Convert
        grst = grsshp_to_grsrst(gshp, inSource, gshp+'__rst', api="grass")

        # Export
        grs_to_rst(grst, outRaster, as_cmd=True)
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return outRaster


def shape_to_rst_wShapeCheck(inShp, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Feature Class to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os
    from glass.pys        import obj_to_lst
    from glass.prop.rst import rst_shape
    
    desiredCellsizes = obj_to_lst(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    workspace = os.path.dirname(outRst)
    
    RASTERS = [shp_to_rst(
        inShp, None, cellsize, -1, os.path.join(
            workspace, f'tst_cell_{str(cellsize)}.tif'
        ), inEPSG
    ) for cellsize in desiredCellsizes]
    
    tstShape = rst_shape(RASTERS)
    
    for rst in tstShape:
        NCELLS = tstShape[rst][0] * tstShape[rst][1]
        tstShape[rst] = NCELLS
    
    NICE_RASTER = None
    for i in range(len(desiredCellsizes)):
        if tstShape[RASTERS[i]] <= maxCellNumber:
            NICE_RASTER = RASTERS[i]
            break
        
        else:
            continue
    
    if not NICE_RASTER:
        return None
    
    else:
        os.rename(NICE_RASTER, outRst)
        
        for rst in RASTERS:
            if os.path.isfile(rst) and os.path.exists(rst):
                os.remove(rst)
        
        return outRst

