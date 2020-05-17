"""
ESRI Shapefile to Something
"""

import arcpy


def shp_to_lyr(s, name=None):
    """
    Create a layer from a feature class data source
    """
    
    import os
    from glass.pys.oss import fprop
    
    lyr = arcpy.MakeFeatureLayer_management(
        s, name if name else fprop(s, 'fn'),
        "", "", ""
    )
    
    return lyr

