"""
Copy data
"""

import arcpy

def copy_feat(inshp, outshp):
    """
    Copy features
    """

    arcpy.CopyFeatures_management(inshp, outshp)

    return outshp

