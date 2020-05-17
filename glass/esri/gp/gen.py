"""
Tools for Geometric Generalization
"""

import arcpy


def dissolve(inShp, outShp, fld, statistics=None, geomMultiPart=True):
    """
    Dissolve Geometries
    """
    
    MULTIPART = "MULTI_PART" if geomMultiPart else "SINGLE_PART"

    nlyr = arcpy.management.Dissolve(
        in_features=inShp, out_feature_class=outShp,
        dissolve_field=fld,
        statistics_fields=statistics
    )
    
    return nlyr

