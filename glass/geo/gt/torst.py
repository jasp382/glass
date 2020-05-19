"""
Data to Raster File
"""

"""
Array to Raster
"""

def obj_to_rst(inArray, outRst, template, noData=None, geotrans=None):
    """
    Send Array to Raster
    
    API Available:
    * gdal;
    """
    
    gisApi = 'gdal'
    
    if gisApi == 'gdal':
        from osgeo            import gdal, osr, gdal_array
        from glass.geo.gt.prop.ff  import drv_name
        from glass.geo.gt.prop.rst import compress_option

        if type(template).__name__ == 'Dataset':
            img_template = template
        else:
            img_template  = gdal.Open(template)
        
        geo_transform = img_template.GetGeoTransform() if not geotrans else \
            geotrans
        rows, cols    = inArray.shape
        drv_n         = drv_name(outRst)
        driver        = gdal.GetDriverByName(drv_n)

        c_opt = compress_option(drv_n)
        if c_opt:
            out       = driver.Create(
                outRst, cols, rows, 1,
                gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype),
                options=[c_opt]
            )
        else:
            out       = driver.Create(
                outRst, cols, rows, 1,
                gdal_array.NumericTypeCodeToGDALTypeCode(inArray.dtype)
            )
        out.SetGeoTransform(geo_transform)
        outBand       = out.GetRasterBand(1)
    
        if noData or noData==0:
            outBand.SetNoDataValue(noData)
        
        outBand.WriteArray(inArray)
        
        proj = osr.SpatialReference(wkt=img_template.GetProjection())
    
        if proj:
            out.SetProjection(img_template.GetProjection())
    
        outBand.FlushCache()
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return outRst


"""
Extent to Raster
"""

def ext_to_rst(topLeft, btRight, outRst,
               cellsize=None, epsg=None, outEpsg=None,
               invalidResultAsNull=None):
    """
    Extent to Raster
    """
    
    import os; import numpy
    from osgeo import ogr, gdal
    from glass.geo.gt.prop.ff import drv_name
    
    left, top     = topLeft
    right, bottom = btRight
    
    cellsize = 10 if not cellsize else cellsize
    
    if outEpsg and epsg and outEpsg != epsg:
        from glass.geo.gm.to  import new_pnt
        from glass.geo.gm.to  import create_polygon
        from glass.geo.gm.prj import prj_ogrgeom
        
        extGeom = prj_ogrgeom(create_polygon([
            new_pnt(left, top), new_pnt(right, top),
            new_pnt(right, bottom), new_pnt(left, bottom), new_pnt(left, top)
        ]), epsg, outEpsg)
        
        left, right, bottom, top = extGeom.GetEnvelope()
    
    # Get row and cols number
    rows = (float(top) - float(bottom)) / cellsize
    cols = (float(right) - float(left)) / cellsize
    
    rows = int(rows) if rows == int(rows) else int(rows) + 1
    cols = int(cols) if cols == int(cols) else int(cols) + 1
    
    if not invalidResultAsNull:
        NEW_RST_ARRAY = numpy.zeros((rows, cols))
    else:
        try:
            NEW_RST_ARRAY = numpy.zeros((rows, cols))
        except:
            return None
    
    # Create new Raster
    img = gdal.GetDriverByName(drv_name(outRst)).Create(
        outRst, cols, rows, 1, gdal.GDT_Byte
    )
    
    img.SetGeoTransform((left, cellsize, 0, top, 0, -cellsize))
    
    band = img.GetRasterBand(1)
    
    band.WriteArray(NEW_RST_ARRAY)
    
    if epsg:
        from osgeo import osr
        
        rstSrs = osr.SpatialReference()
        rstSrs.ImportFromEPSG(epsg)
        img.SetProjection(rstSrs.ExportToWkt())
    
    band.FlushCache()
    
    return outRst


"""
Conversion between formats
"""

def rst_to_rst(inRst, outRst):
    """
    Convert a raster file to another raster format
    """
    
    from glass.pyt            import execmd
    from glass.geo.gt.prop.ff import drv_name
    
    outDrv = drv_name(outRst)
    cmd = 'gdal_translate -of {drv} {_in} {_out}'.format(
        drv=outDrv, _in=inRst, _out=outRst
    )
    
    cmdout = execmd(cmd)
    
    return outRst


def rsts_to_gpkg(in_rsts, gpkg, rst_ff='.tif', basename=None):
    """
    Raster Files to GeoPackage
    """

    import os
    import numpy as np
    from glass.pyt             import execmd
    from glass.pyt.oss         import fprop
    from glass.geo.gt.prop.rst import rst_dtype

    if type(in_rsts) == list:
        rsts = in_rsts
    
    elif os.path.isdir(in_rsts):
        from glass.pyt.oss import lst_ff

        rsts = lst_ff(in_rsts, file_format='.tif' if not rst_ff else rst_ff)
    
    else:
        rsts = [in_rsts]
    
    new_cmd = "gdal_translate -of GPKG {} {} -CO RASTER_TABLE={}{}"
    upd_cmd = (
        "gdal_translate -of GPKG {} {} -co APPEND_SUBDATASET=YES -CO "
        "RASTER_TABLE={}{}"
    )

    for r in range(len(rsts)):
        rst_type = rst_dtype(rsts[r])

        tname = fprop(rsts[r], 'fn') if not basename else \
            "{}_{}".format(basename, fprop(rsts[r], 'fn').split('_')[-1])
        
        if not r and not os.path.exists(gpkg):
            rcmd = execmd(new_cmd.format(
                rsts[r], gpkg, tname,
                " -ot Float32" if rst_type == np.float64 else ""
            ))
        else:
            rcmd = execmd(upd_cmd.format(
                rsts[r], gpkg, tname,
                " -ot Float32" if rst_type == np.float64 else ""
            ))

    return gpkg


def gpkgrst_to_rst(gpkg, tbl, outrst):
    """
    Convert Raster in GeoPackage to single file
    """

    from glass.pyt import execmd
    from glass.geo.gt.prop.ff import drv_name

    rcmd = execmd("gdal_translate -of {} {} {} -b 1 -oo TABLE={}".format(
        drv_name(outrst), gpkg, outrst, tbl
    ))

    return outrst


def rst_to_grs(rst, grsRst, lmtExt=None, as_cmd=None):
    """
    Raster to GRASS GIS Raster
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        __flag = 'o' if not lmtExt else 'or'
        
        m = Module(
            "r.in.gdal", input=rst, output=grsRst, flags='o',
            overwrite=True, run_=False, quiet=True,
        )
        
        m()
    
    else:
        from glass.pyt import execmd
        
        rcmd = execmd((
            "r.in.gdal input={} output={} -o{} --overwrite "
            "--quiet"
        ).format(rst, grsRst, "" if not lmtExt else " -r"))
    
    return grsRst


def grs_to_rst(grsRst, rst, as_cmd=None, allBands=None):
    """
    GRASS Raster to Raster
    """
    
    from glass.geo.gt.prop.ff import grs_rst_drv
    from glass.pyt.oss        import fprop
    
    rstDrv = grs_rst_drv()
    rstExt = fprop(rst, 'ff')
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.out.gdal", input=grsRst, output=rst,
            format=rstDrv[rstExt], flags='c' if not allBands else '',
            createopt="INTERLEAVE=PIXEL,TFW=YES" if allBands else 'TFW=YES',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from glass.pyt import execmd
        
        rcmd = execmd((
            "r.out.gdal input={} output={} format={} "
            "{} -c --overwrite --quiet"
        ).format(
            grsRst, rst, rstDrv[rstExt],
            "createopt=\"TFW=YES\"" if not allBands else \
                "createopt=\"INTERLEAVE=PIXEL,TFW=YES\""
        ))
    
    return rst


def grs_to_mask(inRst):
    """
    Grass Raster to Mask
    """
    
    from grass.pygrass.modules import Module
    
    m = Module('r.mask', raster=inRst, quiet=True, run_=False)
    
    m()


def saga_to_tif(inFile, outFile):
    """
    SAGA GIS format to GeoTIFF
    """
    
    from glass.pyt     import execmd
    from glass.pyt.oss import fprop
    
    # Check if outFile is a GeoTiff
    if fprop(outFile, 'ff') != '.tif':
        raise ValueError(
            'Outfile should have GeoTiff format'
        )
    
    cmd = (
        "saga_cmd io_gdal 2 -GRIDS {} "
        "-FILE {}"
    ).format(inFile, outFile)
    
    outcmd = execmd(cmd)
    
    return outFile


def tif_to_grid(inFile, outFile):
    """
    GeoTiff to SAGA GIS GRID
    """
    
    from glass.pyt import execmd
    
    comand = (
        "saga_cmd io_gdal 0 -FILES {} "
        "-GRIDS {}"
    ).format(inFile, outFile)
    
    outcmd = execmd(comand)
    
    return outFile


def folder_nc_to_tif(inFolder, outFolder):
    """
    Convert all nc existing on a folder to GTiff
    """
    
    import netCDF4;    import os
    from glass.pyt.oss  import lst_ff
    from glass.geo.gt.torst import bands_to_rst
    
    # List nc files
    lst_nc = lst_ff(inFolder, file_format='.nc')
    
    # nc to tiff
    for nc in lst_nc:
        # Check the number of images in nc file
        datasets = []
        _nc = netCDF4.Dataset(nc, 'r')
        for v in _nc.variables:
            if v == 'lat' or v == 'lon':
                continue
            lshape = len(_nc.variables[v].shape)
            if lshape >= 2:
                datasets.append(v)
        # if the nc has any raster
        if len(datasets) == 0:
            continue
        # if the nc has only one raster
        elif len(datasets) == 1:
            output = os.path.join(
                outFolder,
                os.path.basename(os.path.splitext(nc)[0]) + '.tif'
            )
            rst_to_rst(nc, output)
            bands_to_rst(output, outFolder)
        # if the nc has more than one raster
        else:
            for dts in datasets:
                output = os.path.join(
                    outFolder,
                    '{orf}_{v}.tif'.format(
                        orf = os.path.basename(os.path.splitext(nc)[0]),
                        v = dts
                    )
                )
                rst_to_rst(
                    'NETCDF:"{n}":{v}'.format(n=nc, v=dts),
                    output
                )
                bands_to_rst(output, outFolder)


"""
Join Bands
"""

def comp_bnds(rsts, outRst):
    """
    Composite Bands
    """
    
    from osgeo            import gdal, gdal_array
    from glass.geo.gt.fmrst    import rst_to_array
    from glass.geo.gt.prop.ff  import drv_name
    from glass.geo.gt.prop.rst import get_nodata
    from glass.geo.gt.prop.prj import get_rst_epsg, epsg_to_wkt
    
    # Get Arrays
    _as = [rst_to_array(r) for r in rsts]
    
    # Get nodata values
    nds = [get_nodata(r) for r in rsts]
    
    # Assume that first raster is the template
    img_temp = gdal.Open(rsts[0])
    geo_tran = img_temp.GetGeoTransform()
    band = img_temp.GetRasterBand(1)
    dataType = gdal_array.NumericTypeCodeToGDALTypeCode(_as[0].dtype)
    rows, cols = _as[0].shape
    epsg = get_rst_epsg(rsts[0])
    
    # Create Output
    drv = gdal.GetDriverByName(drv_name(outRst))
    out = drv.Create(outRst, cols, rows, len(_as), dataType)
    out.SetGeoTransform(geo_tran)
    out.SetProjection(epsg_to_wkt(epsg))
    
    # Write all bands
    for i in range(len(_as)):
        outBand = out.GetRasterBand(i+1)
        outBand.SetNoDataValue(nds[i])
        outBand.WriteArray(_as[i])
        
        outBand.FlushCache()
    
    return outRst


"""
Feature Class to Raster
"""

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
        from osgeo           import gdal, ogr
        from glass.geo.gt.prop.ff import drv_name
    
        if not epsg:
            from glass.geo.gt.prop.prj import get_shp_sref
            srs = get_shp_sref(shp).ExportToWkt()
        else:
            from glass.geo.gt.prop.prj import epsg_to_wkt
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
                from glass.geo.gt.prop.rst import adjust_ext_to_snap
                
                x_min, y_max, y_res, x_res, cellsize = adjust_ext_to_snap(
                    shp, snapRst
                )
    
        else:
            from glass.geo.gt.fmrst import rst_to_array
        
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
        Vectorial geometry to raster
    
        If source is None, the convertion will be based on the cat field.
    
        If source is a string, the convertion will be based on the field
        with a name equal to the given string.
    
        If source is a numeric value, all cells of the output raster will have
        that same value.
        """
        
        __USE = "cat" if not inSource else "attr" if type(inSource) == str \
            else "val" if type(inSource) == int or \
            type(inSource) == float else None
        
        if not __USE:
            raise ValueError('\'source\' parameter value is not valid')
        
        if api == 'pygrass':
            from grass.pygrass.modules import Module
            
            m = Module(
                "v.to.rast", input=shp, output=outRaster, use=__USE,
                attribute_column=inSource if __USE == "attr" else None,
                value=inSource if __USE == "val" else None,
                overwrite=True, run_=False, quiet=True
            )
            
            m()
        
        else:
            from glass.pyt import execmd
            
            rcmd = execmd((
                "v.to.rast input={} output={} use={}{} "
                "--overwrite --quiet"
            ).format(
                shp, outRaster, __USE,
                "" if __USE == "cat" else " attribute_column={}".format(inSource) \
                    if __USE == "attr" else " val={}".format(inSource)
            ))
    
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
    from glass.pyt         import obj_to_lst
    from glass.geo.gt.prop.rst import rst_shape
    
    desiredCellsizes = obj_to_lst(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    workspace = os.path.dirname(outRst)
    
    RASTERS = [shp_to_rst(
        inShp, cellsize, -1, os.path.join(
            workspace, 'tst_cell_{}.tif'.format(cellSize)
        ), inEPSG
    ) for cellSize in desiredCellsizes]
    
    tstShape = rst_shape(RASTERS, gisApi='gdal')
    
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


def shpext_to_rst(inShp, outRaster, cellsize=None, epsg=None,
                  invalidResultAsNone=None, outEpsg=None):
    """
    Extent to raster
    
    if invalidResultAsNone - if for some reason something went wrong, the 
    result of this method will be a None Object if there is an error on the
    numpy array creation. If False, an error will be raised.
    """
    
    import os;            import numpy
    from osgeo            import ogr, gdal
    from glass.geo.gt.prop.ff  import drv_name
    from glass.geo.gt.prop.ext import get_ext
        
    cellsize = 10 if not cellsize else cellsize
    
    # Get extent
    try:
        left, right, bottom, top = get_ext(inShp)
    except:
        left, right, bottom, top = inShp.GetEnvelope()
    
    return ext_to_rst(
        (left, top), (right, bottom), outRaster,
        cellsize=cellsize, epsg=epsg, outEpsg=outEpsg,
        invalidResultAsNull=invalidResultAsNone
    )


def geomext_to_rst_wShapeCheck(inGeom, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Geometry to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os; from glass.pyt import obj_to_lst
    
    desiredCellsizes = obj_to_lst(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    # Get geom extent
    left, right, bottom, top = inGeom.GetEnvelope()
    
    # Check Rasters Shape for each desired cellsize
    SEL_CELLSIZE = None
    for cellsize in desiredCellsizes:
        # Get Row and Columns Number
        NROWS = int(round((top - bottom) / cellsize, 0))
        NCOLS = int(round((right - left) / cellsize, 0))
        
        NCELLS = NROWS * NCOLS
        
        if NCELLS <= maxCellNumber:
            SEL_CELLSIZE = cellsize
            break
    
    if not SEL_CELLSIZE:
        return None
    
    else:
        shpext_to_rst(
            inGeom, outRst, SEL_CELLSIZE, epsg=inEPSG,
            invalidResultAsNone=True
        )
        
        return outRst


"""
Split Raster
"""


def bands_to_rst(inRst, outFolder):
    """
    Export all bands of a raster to a new dataset
    
    TODO: this could be done using gdal_translate
    """
    
    import numpy;         import os
    from osgeo            import gdal
    from glass.geo.gt.torst    import obj_to_rst
    from glass.geo.gt.prop.rst import get_nodata
    
    
    rst = gdal.Open(inRst)
    
    if rst.RasterCount == 1:
        return
    
    nodata = get_nodata(inRst)
    
    for band in range(rst.RasterCount):
        band += 1
        src_band = rst.GetRasterBand(band)
        if src_band is None:
            continue
        else:
            # Convert to array
            array = numpy.array(src_band.ReadAsArray())
            obj_to_rst(array, os.path.join(
                outFolder, '{r}_{b}.tif'.format(
                    r=os.path.basename(os.path.splitext(inRst)[0]),
                    b=str(band)
                )), inRst, noData=nodata
            )


def rstval_to_binrst(rst, outfld, fileformat=None):
    """
    Export all values in a raster to new binary raster
    """

    import os
    import numpy as np
    from osgeo import gdal
    from glass.geo.gt.torst import obj_to_rst
    from glass.pyt.oss      import fprop

    fileformat = fileformat if fileformat else '.tif'

    rst_src = gdal.Open(rst, gdal.GA_ReadOnly)

    # Get Nodata
    nd = rst_src.GetRasterBand(1).GetNoDataValue()

    # Data To Array
    rst_num = rst_src.GetRasterBand(1).ReadAsArray()

    # Get Unique values in Raster
    val = np.unique(rst_num)
    val = list(val[val != nd])

    fn = fprop(rst, 'fn')
    for v in val:
        # Create new binary array
        val_a = np.zeros(rst_num.shape, dtype=np.uint8)
        np.place(val_a, rst_num == v, 1)

        # Export to new raster
        obj_to_rst(val_a, os.path.join(
            outfld, fn + '_val' + str(v) + fileformat
        ), rst_src, noData=0)
