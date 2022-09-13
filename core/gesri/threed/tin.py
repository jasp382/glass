"""
TIN Operations
"""

import arcpy

def create_tin(outTin, prj, inputStr):
    """
    Execute Create TIN from 3D Analyst Tools
    """
    
    arcpy.CreateTin_3d(outTin, prj, inputStr, "DELAUNAY")

