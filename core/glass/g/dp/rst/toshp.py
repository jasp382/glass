"""
Raster to Feature Class
"""

def rst_to_polyg(inRst, outShp, rstColumn=None, gisApi='gdal', epsg=None):
    """
    Raster to Polygon Shapefile
    
    Api's Available:
    * gdal;
    * qgis;
    * pygrass;
    * grass;
    """
    
    if gisApi == 'gdal':
        if not epsg:
            raise ValueError((
                'Using GDAL, you must specify the EPSG CODE of the '
                'Spatial Reference System of input raster.'
            ))
        
        import os;from osgeo import gdal, ogr, osr
        from glass.g.prop import drv_name
        from glass.pys.oss   import fprop
        
        src = gdal.Open(inRst)
        bnd = src.GetRasterBand(1)
        
        output = ogr.GetDriverByName(drv_name(ouShp)).CreateDataSource(outShp)
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        
        lyr = output.CreateLayer(fprop(outShp, 'fn', forceLower=True), srs)
        
        lyr.CreateField(ogr.FieldDefn('VALUE', ogr.OFTInteger))
        gdal.Polygonize(bnd, None, lyr, 0, [], callback=None)
        
        output.Destroy()
    
    elif gisApi == 'qgis':
        import processing
        
        processing.runalg(
            "gdalogr:polygonize", inRst, "value", outShp
        )
    
    elif gisApi == 'pygrass':
        from grass.pygrass.modules import Module
        
        rstField = "value" if not rstColumn else rstColumn
        
        rtop = Module(
            "r.to.vect", input=inRst, output=outShp, type="area",
            column=rstField, overwrite=True, run_=False, quiet=True
        )
        rtop()
    
    elif gisApi == 'grass':
        from glass.pys import execmd
        
        rstField = "value" if not rstColumn else rstColumn
        
        rcmd = execmd((
            "r.to.vect input={} output={} type=area column={} "
            "--overwrite --quiet"
        ).format(inRst, outShp, rstField))
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp


def rst_to_pnt(in_rst, out_pnt):
    """
    Raster to Point Feature Class
    """

    from glass.g.wt.shp import df_to_shp

    api = 'pandas'

    if api == 'pandas':
        from glass.g.rd.rst import rst_to_geodf

        gdf = rst_to_geodf(in_rst)

        df_to_shp(gdf, out_pnt)
    
    else:
        raise ValueError('API {} is not available'.format(api))

    return out_pnt


def rsts_to_shps(rstfolder, outfolder, rsttemplate):
    """
    Rasters in folder to Shapefile

    this script uses GRASS GIS
    """

    import os
    from glass.pys.oss    import lst_ff, fprop
    from glass.g.wenv.grs import run_grass

    # List Raster Files
    rsts = lst_ff(rstfolder, file_format='tif')

    # Start GRASS GIS Session
    loc='convrst'
    grsbase = run_grass(outfolder, location=loc, srs=rsttemplate)

    import grass.script.setup as gsetup

    gsetup.init(grsbase, outfolder, loc, 'PERMANENT')

    from glass.g.it.rst import rst_to_grs
    from glass.g.it.shp import grs_to_shp

    for rst in rsts:
        grs_rst = rst_to_grs(rst, fprop(rst, 'fn'), as_cmd=True)

        # to polygon
        grs_shp = rst_to_polyg(
            grs_rst, grs_rst + "_shp",
            rstColumn="value", gisApi='grasscmd'
        )

        grs_to_shp(grs_shp, os.path.join(
            outfolder, grs_rst + '.shp'
        ), 'area')
    
    return outfolder
