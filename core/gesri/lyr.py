"""
Deal with Layer Objects
"""

import arcpy

""" *********** Feature Classes *********** """


""" *********** Raster Datasets *********** """
def rst_lyr(r):
    import os
    
    lyr = arcpy.MakeRasterLayer_management(
        r,
        os.path.splitext(os.path.basename(r))[0],
        "", "", "1"
    )
    return lyr

def checkIfRstIsLayer(obj):
    """
    Check if an object is a Raster Layer
    """
    
    dataType = arcpy.Describe(obj)
    
    return True if dataType == u'RasterLayer' else None
