"""
Something to raster using ArcGIS tools
"""

import arcpy


"""
Shape To Raster
"""

def shp_to_rst(shp, inField, cellsize, outRaster, template=None, snap=None):
    """
    Feature Class to Raster
    """
    
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
        
    if snap:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snap
        
    obj_describe = arcpy.Describe(shp)
    geom = obj_describe.ShapeType
        
    if geom == 'Polygon':
        arcpy.PolygonToRaster_conversion(
            shp, inField, outRaster, "CELL_CENTER",
            "NONE", str(cellsize)
        )
        
    elif geom == 'Polyline':
        arcpy.PolylineToRaster_conversion(
            shp, inField, outRaster, "MAXIMUM_LENGTH",
            "NONE", str(cellsize)
        )
        
    if template:
        arcpy.env.extent = tempEnvironment0
        
    if snap:
        arcpy.env.snapRaster = tempSnap

"""
TIN TO RASTER
"""

def tin_to_raster(tin, cs, out, template=None, snapRst=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    if snapRst:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snapRst
    
    arcpy.TinRaster_3d(
        tin, out, "FLOAT", "LINEAR", "CELLSIZE {}".format(str(cs)), "1"
    )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    if snapRst:
        arcpy.env.snapRaster = tempSnap
    
    return out


