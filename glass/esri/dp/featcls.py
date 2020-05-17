"""
Feature Classes
"""

import arcpy

def create_feat_class(feature_class, geom, prj):
    """
    Create a new Feature Class
    """
    
    import os
    
    if type(prj) == int:
        from gesri.prop.prj import get_wkt_esri
        __prj = get_wkt_esri(prj)
    
    else:
        __prj = prj
    
    arcpy.CreateFeatureclass_management(
        out_path=os.path.dirname(feature_class),
        out_name=os.path.basename(feature_class), 
        geometry_type=geom,
        spatial_reference=__prj
    )
    
    return feature_class
