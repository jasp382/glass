"""
Table Joins
"""

import arcpy

from glass.pys import obj_to_lst


def join_table(inshp, jshp, pk, fk, cols=None):
    """
    Join Tables using JoinField tool
    """

    cols = obj_to_lst(cols)

    cols = "" if not cols else cols

    res = arcpy.management.JoinField(
        in_data=inshp, in_field=pk,
        join_table=jshp, join_field=fk,
        fields=cols
    )[0]

    return res


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
