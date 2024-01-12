"""
Manage data values in a Raster
"""

import arcpy


def rcls_rst(rst, fld, rules, out, ref, isrange=None):
    """
    Reclassify a raster
    
    https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/reclassify.htm
    """
    
    from arcpy.sa import Reclassify, RemapValue, RemapRange
    
    arcpy.env.extent = ref
    arcpy.env.snapRaster = ref

    remap = RemapValue(rules) if not isrange else \
        RemapRange(rules)
    
    orcls = Reclassify(rst, fld, remap, "NODATA")

    orcls.save(out)
    
    arcpy.env.extent = None
    arcpy.env.snapRaster = None
    
    return out, orcls


def rcls_folderRaster(rstFolder, rules, out):
    """
    Reclassify in loop for all rasters in a folder
    
    Same field, same rules for all rasters
    """
    
    import os
    
    arcpy.env.workspace = rstFolder
    
    rasters = arcpy.ListRasters()
    
    for raster in rasters:
        rcls_rst(
            os.path.join(rstFolder, raster), "Value", rules,
            os.path.join(out, raster), template=raster
        )
    
    return out




