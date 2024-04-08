"""
Merge, combine and mosaic
"""

import os
import arcpy


def mosaic_to_raster(lrst, out, cell, method, refrst=None,
                     pixel_type="8_BIT_UNSIGNED"):
    """
    Merges multiple raster datasets into a new raster dataset.

    https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/mosaic-to-new-raster.htm
    """
    
    if refrst:
        arcpy.env.extent = refrst
        arcpy.env.snapRaster = refrst
    
    
    arcpy.MosaicToNewRaster_management(
        ";".join(lrst), os.path.dirname(out),
        os.path.basename(out),
        "", pixel_type, cell, "1",
        method, "FIRST"
    )
    
    if refrst:
        arcpy.env.extent = None
        arcpy.env.snapRaster = None
    
    return out

