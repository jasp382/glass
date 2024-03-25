"""
ArcGIS Buffering Tools
"""


import arcpy


def bbuffer(inShp, radius, outShp, dissolve=None):
    """
    Buffering on Shapefile
    """
    
    diss = "NONE" if not dissolve else "LIST" if dissolve != "ALL" and \
        dissolve != "NONE" else dissolve
    
    diss_cols = None if dissolve != "LIST" else dissolve
    
    bflyr = arcpy.analysis.Buffer(
        in_features=inShp,
        out_feature_class=outShp,
        buffer_distance_or_field=radius,
        line_side="FULL",
        line_end_type="ROUND",
        dissolve_option=diss,
        dissolve_field=diss_cols,
        method="PLANAR"
    )[0]
    
    return bflyr

