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
        nlyr = arcpy.management.SelectLayerByAttribute(
            inShp, "NEW_SELECTION", sql
        )[0]

        return nlyr


def clear_sel(ilyr):
    """
    Clear selection
    """

    nlyr = arcpy.management.SelectLayerByAttribute(
        ilyr, "CLEAR_SELECTION", None
    )[0]

    return nlyr

