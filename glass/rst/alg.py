"""
Algebra tools
"""


def gdal_mapcalc(expression, exp_val_paths, outRaster, template_rst,
    outNodata=-99999):
    """
    GDAL Raster Calculator
    
    TODO: Check if rasters dimensions are equal
    """
    
    import numpy            as np
    from osgeo              import gdal
    from py_expression_eval import Parser
    from glass.prop.img   import get_nd
    from glass.wt.rst     import obj_to_rst
    
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
        from glass.pys      import execmd
        from glass.pys.oss  import fprop
        from glass.it.rst import saga_to_tif
        
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
            f'{output} = {expression}',
            overwrite=True, run_=False, quiet=True
        )
        
        rc()
    
    elif api == 'grass':
        from glass.pys  import execmd
        
        rcmd = execmd((
            f"r.mapcalc \"{output} = {expression}\" "
            "--overwrite --quiet"
        ))
    
    else:
        raise ValueError(f"{api} is not available!")
    
    return output


"""
Expression's
"""

def repnd_by_rstval(ref_rst, val_rst, out_rst):
    """
    Replace NoData Values with values from another raster
    """

    import numpy as np
    from osgeo import gdal
    from glass.wt.rst import obj_to_rst

    # TODO check if shape of two rasters are the same

    # Open Rasters and Get data as array
    refsrc = gdal.Open(ref_rst, gdal.GA_ReadOnly)
    popsrc = gdal.Open(val_rst, gdal.GA_ReadOnly)

    nd_val = refsrc.GetRasterBand(1).GetNoDataValue()
    nd_pop = refsrc.GetRasterBand(1).GetNoDataValue()

    refnum = refsrc.GetRasterBand(1).ReadAsArray()
    popnum = popsrc.GetRasterBand(1).ReadAsArray()

    # Replace NoData Values
    np.copyto(refnum, popnum, where=refnum==nd_val)

    # Export to file
    obj_to_rst(refnum, out_rst, refsrc, noData=nd_pop)

    return out_rst

