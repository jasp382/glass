"""
Feature Class Properties
"""

import arcpy

def get_gtype(fc):
    """
    Return GEOMETRY TYPE of one feature class
    """
    
    return arcpy.Describe(fc).ShapeType

def feat_count(shp):
    """
    Count the number of features in a feature class
    """
    
    return int(arcpy.GetCount_management(lyr).getOutput(0))


def get_ext(shp):
    """
    Return extent of a Vectorial file
    
    Return a tuple object with the follow order:
    (left, right, bottom, top)
    """
    
    descObj = arcpy.Describe(shp)
        
    EXT = [
        descObj.extent.XMin, descObj.extent.XMax,
        descObj.extent.YMin, descObj.extent.YMax
    ]
    
    return EXT


"""
Single Features
"""

def get_feat_area(instance, shapeFld):
    return float(instance.getValue(shapeFld).area)

