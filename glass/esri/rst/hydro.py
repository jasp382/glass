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
    """
    Run Flow Direction

    https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/flow-direction.htm
    """

    from arcpy.sa import FlowDirection

    arcpy.env.extent = mdt
    arcpy.env.snapRaster = mdt

    odir = FlowDirection(mdt, "NORMAL", "", "D8")

    odir.save(output)
    
    arcpy.env.extent = None
    arcpy.env.snapRaster = None
    
    return output, odir


def flow_accumulation(direction, output):
    """
    Run Flow Accumulation

    https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/flow-accumulation.htm
    """

    from arcpy.sa import FlowAccumulation

    arcpy.env.extent = direction
    arcpy.env.snapRaster = direction

    acc = FlowAccumulation(direction, "", "FLOAT", "D8")

    acc.save(output)
    
    return output, acc


def stream_to_feature(hydro, direction, output):
    arcpy.gp.StreamToFeature_sa(hydro, direction, output,
                                "SIMPLIFY")
    
    return output

