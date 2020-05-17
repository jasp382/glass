"""
Raster calculator options
"""

import arcpy

def rstcalc(expression, output, template=None):
    """
    Basic Raster Calculator
    """
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.RasterCalculator_sa(expression, output)
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return output


def floatRst_to_IntegerRst(inFolder, outFolder):
    """
    List all folders in a folder and convert them to integer
    """
    
    import os
    from gesri.lyr import rst_lyr
    
    arcpy.env.workspace = inFolder
    
    rasters = arcpy.ListRasters()
    
    for rst in rasters:
        lyr = rst_lyr(os.path.join(inFolder, rst))
        
        rstcalc(
            'Int("{}")'.format(os.path.splitext(rst)[0]),
            os.path.join(outFolder, rst),
            template=os.path.join(inFolder, rst)
        )

