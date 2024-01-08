"""
Table Joins
"""

import arcpy



def spatial_join(inShp, joinShp, outShp, attr=None):
    """
    Join two tables based in spatial relation
    """
    
    import os
    from glass.pys import obj_to_lst
    
    attr = obj_to_lst(attr)
    
    if attr:
        ATTR = [(
            "{fld} \"{fld}\" true true false 30 Text 0 0 ,"
            "First,#,{shp},{fld},-1,-1"
        ).format(
            fld=x, shp=os.path.splitext(os.path.basename(joinShp))[0]
        ) for x in attr]
    
    else:
        ATTR = ""
    
    arcpy.SpatialJoin_analysis(
        inShp, joinShp, outShp, "JOIN_ONE_TO_ONE", "KEEP_ALL",
        ";".join(ATTR), "INTERSECT", "", ""
    )
    
    return outShp
