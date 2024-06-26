"""
Algebra tools
"""

import numpy as np
from osgeo import gdal

from glass.pys      import execmd
from glass.prop.img import rst_epsg, get_nd
from glass.wt.rst   import obj_to_rst


def gdal_mapcalc(expression, exp_val_paths, outRaster, template_rst,
    outNodata=-99999):
    """
    GDAL Raster Calculator
    
    TODO: Check if rasters dimensions are equal
    """
    
    from py_expression_eval import Parser
    
    parser = Parser()
    
    EXPRESSION = parser.parse(expression)
    
    evalValue, noDatas = {}, {}

    gtrans, epsg = None, None

    for x in EXPRESSION.variables():
        img = gdal.Open(exp_val_paths[x])

        if not gtrans:
            gtrans = img.GetGeoTransform()
        
        if not epsg:
            epsg = rst_epsg(img)
        
        arr = img.ReadAsArray().astype(float)
        
        evalValue[x] = arr
        noDatas[x]   = get_nd(img)
    
    result = EXPRESSION.evaluate(evalValue)
    
    for v in noDatas:
        np.place(result, evalValue[v]==noDatas[v], outNodata)
    
    # Write output and return
    
    return obj_to_rst(result, outRaster, template_rst, noData=outNodata)


def grsrstcalc(expression, result, ascmd=None):
    """
    GRASS GIS Raster Calculator
    """

    if not ascmd:
        from grass.pygrass.modules import Module

        rc = Module(
            'r.mapcalc',
            f'{result} = {expression}',
            overwrite=True, run_=False, quiet=True
        )

        rc()
    
    else:
        rcmd = execmd((
            f"r.mapcalc \"{result} = {expression}\" "
            "--overwrite --quiet"
        ))
    
    return result


def gdalrstcalc(irsts, expression, result, odtype=None):
    """
    GDAL Raster Calculator
    """

    irsts_str = " ".join([f"-{k} {irsts[k]}" for k in irsts])

    otype = "" if not odtype else f' --type={odtype}'

    cmd = (
        f"gdal_calc.py {irsts_str} --outfile={result} "
        f"--calc=\"{expression}\"{otype}"
    )

    ocmd = execmd(cmd)

    return result


def rstcalc(expression, output, api='saga', grids=None):
    """
    Basic Raster Calculator
    """

    import os
    from glass.pys.oss import fprop
    
    if api == 'saga':
        # Using SAGA GIS
        from glass.it.rst import saga_to_tif
        
        SAGA_RASTER = os.path.join(
            os.path.dirname(output),
            f"sag_{fprop(output, 'fn')}.sgrd"
        )
        
        cmd = (
            f"saga_cmd grid_calculus 1 -FORMULA \"{expression}\" "
            f"-GRIDS \"{';'.join(grids)}\" "
            f"-RESULT {SAGA_RASTER} -RESAMPLING 0"
        )
        
        outcmd = execmd(cmd)
        
        # Convert to tiff
        saga_to_tif(SAGA_RASTER, output)
    
    elif api == 'grass' or api == "pygrass":
        from glass.wenv.grs import run_grass
        from glass.pys      import obj_to_lst
        from glass.pys.tm import now_as_str
        
        or_name = fprop(output, 'fn')

        ws, loc = os.path.dirname(output), now_as_str()

        rsts = obj_to_lst(grids)

        gb = run_grass(ws, grassBIN="grass78", location=loc, srs=rsts[0])

        import grass.script.setup as gsetup

        gsetup.init(gb, ws, loc, 'PERMANENT')

        from glass.it.rst import rst_to_grs, grs_to_rst

        # Import rsts
        grsts = [rst_to_grs(r) for r in rsts]

        # Do the math
        out = grsrstcalc(
            expression, or_name,
            ascmd=True if api == "grass" else None
        )

        # Export
        grs_to_rst(or_name, output, as_cmd=None, rtype=float)
    
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
    obj_to_rst(
        refnum, out_rst,
        refsrc.GetGeoTransform(), rst_epsg(refsrc),
        noData=nd_pop
    )

    return out_rst

