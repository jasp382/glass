"""
Raster calculator options
"""

import arcpy

def rstcalc(rasters, names, expression, output, template=None):
    """
    Basic Raster Calculator
    """

    from arcpy.sa import RasterCalculator
    
    if template:
        arcpy.env.extent = template
        arcpy.env.snapRaster = template
    
    calcres = RasterCalculator(rasters, names, expression, "FirstOf", "FirstOf")
    calcres.save(output)
    
    if template:
        arcpy.env.extent = None
        arcpy.env.snapRaster = None
    
    return output, calcres


def floatRst_to_IntegerRst(inFolder, outFolder):
    """
    List all folders in a folder and convert them to integer
    """
    
    import os
    from glass.esri.rd.rst import rst_to_lyr
    
    arcpy.env.workspace = inFolder
    
    rasters = arcpy.ListRasters()
    
    for rst in rasters:
        rst_to_lyr(os.path.join(inFolder, rst))
        
        rstcalc(
            f'Int("{os.path.splitext(rst)[0]}")',
            os.path.join(outFolder, rst),
            template=os.path.join(inFolder, rst)
        )


def set_null(rst, val, orst, refrst=None, operator='='):
    """
    Set raster values to null
    """

    from arcpy.sa import SetNull


    if refrst:
        arcpy.env.extent     = refrst
        arcpy.env.snapRaster = refrst
    
    snres = SetNull(rst, rst, f"VALUE {operator} {val}")
    snres.save(orst)

    if refrst:
        arcpy.env.extent = None
        arcpy.env.snapRaster = None
    
    return orst, snres


def is_null(rst, orst, refrst=None):
    """
    ID Null Values in a Raster
    """

    from arcpy.sa import IsNull

    if refrst:
        arcpy.env.extent     = refrst
        arcpy.env.snapRaster = refrst
    
    snres = IsNull(rst)
    snres.save(orst)
    

    if refrst:
        arcpy.env.extent = None
        arcpy.env.snapRaster = None
    
    return orst, snres

