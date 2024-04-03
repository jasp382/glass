"""
Mapping Layer Fields
"""

import arcpy


def list_fields(lyr):
    """
    List fields of a mapping.layer
    
    (mapping.layer is not the same that featureClassLayer)
    """
    
    cols = arcpy.Describe(lyr).fields
    
    return [col.name for col in cols]

