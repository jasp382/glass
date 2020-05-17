"""
ArcGIS Tools from Spatial Analyst Tools > Hidrology
"""

import arcpy


def fill(mdt, output, template=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.Fill_sa(mdt, output, "")
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return output


def flow_direction(mdt, output):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.FlowDirection_sa(mdt, output, "NORMAL", "")
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return output


def flow_accumulation(direction, output):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    arcpy.gp.FlowAccumulation_sa(direction, output, "", "FLOAT")
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    return output


def stream_to_feature(hydro, direction, output):
    arcpy.gp.StreamToFeature_sa(hydro, direction, output,
                                "SIMPLIFY")
    
    return output

