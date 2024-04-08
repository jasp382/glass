"""
Something to raster using ArcGIS tools
"""

import arcpy


"""
Shape To Raster
"""

def shp_to_rst(shp, incol, csize, orst, template=None, snap=None):
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
        rstlyr = arcpy.conversion.PolygonToRaster(
            shp, incol, orst,
            "CELL_CENTER", cellsize=csize
        )
        
    elif geom == 'Polyline':
        rstlyr = arcpy.conversion.PolylineToRaster(
            shp, incol, orst, "MAXIMUM_LENGTH",
            "NONE", csize
        )
    
    else:
        raise ValueError("Invalid Geometry")
        
    if template:
        arcpy.env.extent = tempEnvironment0
        
    if snap:
        arcpy.env.snapRaster = tempSnap
    

    return orst, rstlyr

