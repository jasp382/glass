"""
Tools for Geometric Generalization
"""

def dissolve(inShp, outShp, fld, statistics=None, geomMultiPart=True):
    """
    Dissolve Geometries
    """
    
    import arcpy
    
    stat = "" if not statistics else statistics
    
    MULTIPART = "MULTI_PART" if geomMultiPart else "SINGLE_PART"
    
    arcpy.Dissolve_management(inShp, outShp, fld, stat, MULTIPART, "")
    
    return outShp

