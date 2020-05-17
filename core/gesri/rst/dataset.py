import arcpy


def mosaic_to_raster(lstRst, out, w, cell, operator, template=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.MosaicToNewRaster_management(
        ";".join(lstRst), w, out,
        "", "8_BIT_UNSIGNED", cell, "1", operator, "FIRST"
    )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return out

