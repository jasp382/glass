"""
Table Joins
"""

import arcpy


def join_tbl(f_tbl, f_f, s_tbl, f_s, fld_to_f_tbl=""):
    arcpy.JoinField_management(
        f_tbl, f_f, s_tbl, f_s, fld_to_f_tbl
    )


def join_table_with_tables(table, idTable, join_tables, join_fields=None):
    """
    Join table with all tables referred in join_tables
    
    join_tables = {
        table_name : join_field_name
        ...
    }
    
    join_fields specify the fields from the join table to add in table
    join_fields = {
        table_name : field,
        table_name : [field_1, field_2, ...]
    }
    """
    from glass.pys import obj_to_lst
    
    for tbl in join_tables:
        if join_fields:
            if tbl in join_fields:
                fld_to_join = obj_to_lst(join_fields[tbl])
            else:
                fld_to_join = ""
        else:
            fld_to_join = ""
        
        join_table(
            table, idTable, tbl, join_tables[tbl],
            fld_to_f_tbl=fld_to_join
        )


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
