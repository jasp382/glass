"""
Data to Raster File
"""


"""
Data type conversion
"""

def conv_rst_dtype(rst, out, odtype):
    """
    Change Raster Dtype

    odtype options:
    * byte
    * int8
    * uint8
    * int16
    * uint16
    * int32
    * uint32
    * float32
    """

    import numpy as np
    from osgeo import gdal
    from glass.wt.rst import obj_to_rst
    
    # Open Raster
    src = gdal.Open(rst, gdal.GA_ReadOnly)
    imgnum = src.ReadAsArray()

    # Get nodata value
    ndval = src.GetRasterBand(1).GetNoDataValue()

    # Get new data type
    if odtype == 'int8':
        dt = np.int8
        ndval = int(ndval)

    elif odtype == 'uint8':
        dt = np.uint8
        ndval = int(ndval)

    elif odtype == 'int16':
        dt = np.int16
        ndval = int(ndval)

    elif odtype == 'uint16':
        dt = np.uint16
        ndval = int(ndval)

    elif odtype == 'int32':
        dt = np.int32
        ndval = int(ndval)

    elif odtype == 'uint32':
        dt = np.uint32
        ndval = int(ndval)
    
    elif odtype == 'float32':
        dt = np.float32
        ndval = float(ndval)
    
    elif odtype == 'byte':
        dt = np.byte
        ndval = int(ndval)
    
    else:
        dt = np.float32
        ndval = float(ndval)

    # Data type conversion
    newnum = imgnum.astype(dt)

    # Export new raster
    obj_to_rst(newnum, out, src, noData=ndval)

    return out


def floatrst_to_intrst(in_rst, out_rst):
    """
    Raster with float data to Raster with Integer Values
    """

    import numpy          as np
    from osgeo            import gdal
    from glass.prop.img import get_nd
    from glass.wt.rst   import obj_to_rst

    nds = {
        'int8' : -128, 'int16' : -32768, 'int32' : -2147483648,
        'uint8' : 255, 'uint16' : 65535, 'uint32' : 4294967295
    }

    # Open Raster
    img = gdal.Open(in_rst)

    # Raster to Array
    rstnum = img.ReadAsArray()

    # Round data
    rstint = np.around(rstnum, decimals=0)

    # Get min and max
    tstmin = rstint.min()
    tstmax = rstint.max()

    try:
        nd = int(round(get_nd(img), 0))
    except:
        nd = None

    if tstmin == nd:
        np.place(rstint, rstint == nd, np.nan)
        rstmin = rstint.min()
        rstmax = tstmax
    else:
        rstmin = tstmin
    
        if tstmax == nd:
            np.place(rstint, rstint == nd, np.nan)
            rstmax = rstint.max()
        else:
            rstmax = tstmax
    
    # Get dtype for output raster
    if rstmin < 0:
        if rstmin <= -128:
            if rstmin <= -32768:
                tmin = 'int32'
            else:
                tmin = 'int16'
        else:
            tmin = 'int8'
    else:
        tmin = 'u'
    
    if tmin == 'u':
        if rstmax >= 255:
            if rstmax >= 65535:
                tmax = 'uint32'
            else:
                tmax = 'uint16'
        else:
            tmax = 'uint8'

    else:
        if tmin == 'int8':
            if rstmax >= 127:
                if rstmax >= 32767:
                    tmax = 'int32'
                else:
                    tmax = 'int16'
            else:
                tmax = 'int8'
    
        elif tmin == 'int16':
            if rstmax >= 32767:
                tmax = 'int32'
            else:
                tmax = 'int16'
        else:
            tmax = 'int32'
    
    if tmax == 'int8':
        nt = np.int8
    elif tmax == 'int16':
        nt = np.int16
    elif tmax == 'int32':
        nt = np.int32
    elif tmax == 'uint8':
        nt = np.uint8
    elif tmax == 'uint16':
        nt = np.uint16
    else:
        nt = np.uint32
    
    # Get nodata for new raster
    new_nd = nds[tmax]
    
    # Place NoData value
    np.nan_to_num(rstint, copy=False, nan=new_nd)

    # Convert array type to integer
    rstint = rstint.astype(nt)

    # Export result to file and return
    return obj_to_rst(rstint, out_rst, img, noData=new_nd)


"""
Conversion between formats
"""

def rst_to_rst(inRst, outRst):
    """
    Convert a raster file to another raster format
    """
    
    from glass.pys    import execmd
    from glass.prop import drv_name
    
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
    from glass.pys        import execmd
    from glass.pys.oss    import fprop
    from glass.prop.rst import rst_dtype

    if type(in_rsts) == list:
        rsts = in_rsts
    
    elif os.path.isdir(in_rsts):
        from glass.pys.oss import lst_ff

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

    from glass.pys import execmd
    from glass.prop import drv_name

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
        from glass.pys import execmd
        
        rcmd = execmd((
            "r.in.gdal input={} output={} -o{} --overwrite "
            "--quiet"
        ).format(rst, grsRst, "" if not lmtExt else " -r"))
    
    return grsRst


def grs_to_rst(grsRst, rst, as_cmd=None, allBands=None):
    """
    GRASS Raster to Raster
    """
    
    from glass.prop  import grs_rst_drv
    from glass.pys.oss import fprop
    
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
        from glass.pys import execmd
        
        rcmd = execmd((
            "r.out.gdal input={} output={} format={} "
            "{} -c --overwrite --quiet"
        ).format(
            grsRst, rst, rstDrv[rstExt],
            "createopt=\"TFW=YES\"" if not allBands else \
                "createopt=\"INTERLEAVE=PIXEL,TFW=YES\""
        ))
    
    return rst


def grs_to_mask(inRst, overwrite=None):
    """
    Grass Raster to Mask
    """

    ow = True if overwrite else False
    
    from grass.pygrass.modules import Module
    
    m = Module(
        'r.mask', raster=inRst,
        overwrite=ow, quiet=True, run_=False
    )
    
    m()


def saga_to_tif(inFile, outFile):
    """
    SAGA GIS format to GeoTIFF
    """
    
    from glass.pys     import execmd
    from glass.pys.oss import fprop
    
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
    
    from glass.pys import execmd
    
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
    from glass.pys.oss  import lst_ff
    from glass.it.rst import bands_to_rst
    
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
    from glass.rd.rst    import rst_to_array
    from glass.prop  import drv_name
    from glass.prop.rst import get_nodata
    from glass.prop.prj import get_rst_epsg, epsg_to_wkt
    
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
Split Raster
"""


def bands_to_rst(inRst, outFolder):
    """
    Export all bands of a raster to a new dataset
    
    TODO: this could be done using gdal_translate
    """
    
    import numpy;         import os
    from osgeo            import gdal
    from glass.wt.rst   import obj_to_rst
    from glass.prop.rst import get_nodata
    
    
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


def rst_to_tiles(rst, n_tiles_x, n_tiles_y, out_folder):
    """
    Raster file to tiles
    """

    import os
    from glass.pys.oss import fprop
    from osgeo import gdal
    from glass.wt.rst import obj_to_rst

    rstprop = fprop(rst, ['fn', 'ff'])
    rstn, rstf = rstprop['filename'], rstprop['fileformat']

    # Open Raster
    img = gdal.Open(rst, gdal.GA_ReadOnly)

    # Get raster Geo Properties
    geotrans = img.GetGeoTransform()

    # Get rows and columns number of original raster
    nrows, ncols = img.RasterYSize, img.RasterXSize

    # Get rows and columns number for the tiles
    tile_rows = int(nrows / n_tiles_y)
    tile_cols = int(ncols / n_tiles_x)

    if tile_rows == nrows / n_tiles_y:
        remain_rows = 0
    else:
        remain_rows = nrows - (tile_rows * n_tiles_y)
    
    if tile_cols == ncols / n_tiles_x:
        remain_cols = 0
    else:
        remain_cols = ncols - (tile_cols * n_tiles_x)
    
    # Create news raster
    rst_num = img.GetRasterBand(1).ReadAsArray()
    nd = img.GetRasterBand(1).GetNoDataValue()

    for tr in range(n_tiles_y):
        if tr + 1 == n_tiles_y:
            __tile_rows = tile_rows + remain_rows
        else:
            __tile_rows = tile_rows
        
        top = geotrans[3] + (geotrans[5] * (tr * tile_rows))

        for tc in range(n_tiles_x):
            if tc + 1 == n_tiles_x:
                __tile_cols = tile_cols + remain_cols
            
            else:
                __tile_cols = tile_cols
            
            left = geotrans[0] + (geotrans[1] * (tc * tile_cols))

            nr = rst_num[
                tr * tile_rows : tr * tile_rows + __tile_rows,
                tc * tile_cols : tc * tile_cols + __tile_cols
            ]

            # New array to file
            obj_to_rst(nr, os.path.join(
                out_folder, rstn + '_' + str(tr) + '_' + str(tc) + rstf 
            ), img, noData=nd, geotrans=(
                left, geotrans[1], geotrans[2], top, geotrans[4], geotrans[5]
            ))

    return out_folder
