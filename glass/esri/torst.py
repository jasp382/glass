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




