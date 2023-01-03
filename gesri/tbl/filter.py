"""
Arcpy tools for information/data extraction
"""

import arcpy


def sel_by_attr(inShp, sql, outShp=None):
    """
    Select data by attributes and write it to file
    """
    
    if outShp:
        arcpy.Select_analysis(inShp, outShp, sql)

        return outShp
    
    else:
        nlyr = arcpy.SelectLayerByAttribute_management(
            inShp, "NEW_SELECTION", sql
        )

        return nlyr

