"""
Algebra tools
"""


def gdal_mapcalc(expression, exp_val_paths, outRaster, template_rst,
    outNodata=-99999):
    """
    GDAL Raster Calculator
    
    TODO: Check if rasters dimensions are equal
    """
    
    import numpy as np
    import os; from osgeo   import gdal, osr
    from glass.geo.gt.prop.ff    import drv_name
    from py_expression_eval import Parser
    from glass.geo.gm.prop.img    import get_nd
    from glass.geo.gt.torst     import obj_to_rst
    
    parser = Parser()
    
    EXPRESSION = parser.parse(expression)
    
    evalValue = {}
    noDatas   = {}
    for x in EXPRESSION.variables():
        img = gdal.Open(exp_val_paths[x])
        arr = img.ReadAsArray().astype(float)
        
        evalValue[x] = arr
        noDatas[x]   = get_nd(img)
    
    result = EXPRESSION.evaluate(evalValue)
    
    for v in noDatas:
        np.place(result, evalValue[v]==noDatas[v], outNodata)
    
    # Write output and return
    
    return obj_to_rst(result, outRaster, template_rst, noData=outNodata)


def rstcalc(expression, output, api='saga', grids=None):
    """
    Basic Raster Calculator
    """
    
    if api == 'saga':
        # Using SAGA GIS
        
        import os
        from glass.pyt          import execmd
        from glass.pyt.oss      import fprop
        from glass.geo.gt.torst import saga_to_tif
        
        SAGA_RASTER = os.path.join(
            os.path.dirname(output),
            "sag_{}.sgrd".format(fprop(output, 'fn'))
        )
        
        cmd = (
            "saga_cmd grid_calculus 1 -FORMULA \"{}\" -GRIDS \"{}\" "
            "-RESULT {} -RESAMPLING 0"
        ).format(
            expression, ";".join(grids), SAGA_RASTER
        )
        
        outcmd = execmd(cmd)
        
        # Convert to tiff
        saga_to_tif(SAGA_RASTER, output)
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        rc = Module(
            'r.mapcalc',
            '{} = {}'.format(output, expression),
            overwrite=True, run_=False, quiet=True
        )
        
        rc()
    
    elif api == 'grass':
        from glass.pyt import execmd
        
        rcmd = execmd((
            "r.mapcalc \"{} = {}\" --overwrite --quiet"
        ).format(output, expression))
    
    else:
        raise ValueError("{} is not available!".format(api))
    
    return output


def floatrst_to_intrst(in_rst, out_rst):
    """
    Raster with float data to Raster with Integer Values
    """

    import numpy         as np
    from osgeo           import gdal
    from glass.geo.gm.prop.img import get_nd
    from glass.geo.gt.torst  import obj_to_rst

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
