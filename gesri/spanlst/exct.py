"""
Spatial Analyst - Extraction tools
"""

import arcpy


def rstval_to_pnt(rst, pnt):
    """
    Extract Raster data to Points
    """
    
    arcpy.sa.ExtractMultiValuesToPoints(pnt, rst, "BILINEAR")

