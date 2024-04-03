"""
Clean table data with arcGIS
"""

import arcpy


def round_table_values(table, decimal_by_col_file, outputFile):
    """
    Round all column values using the number of decimal places written
    in a excel file
    
    COL_NAME | nr_decimal_places
    COL_1    | 1
    COL_2    | 0
    ...      | ...
    COL_N    | 2
    """
    
    from glass.esri.rd.shp    import shp_to_lyr
    from glass.esri.dp        import copy_feat
    from glass.esri.prop.cols import type_fields
    from glass.rd            import tbl_to_obj
    
    arcpy.env.overwriteOutput = True
    
    # Get number of decimal places for the values of each column
    places_by_col = tbl_to_obj(
        decimal_by_col_file, sheet=0, output='dict', useFirstColAsIndex=True
    )
    
    PLACES_FIELD = places_by_col[places_by_col.keys()[0]].keys()[0]
    
    # Copy table
    outTable = copy_feat(table, outputFile, gisApi='arcpy')
    
    # Edit copy putting the correct decimal places in each column
    lyr = shp_to_lyr(outTable)
    
    # List table fields
    fields = type_fields(lyr)
    cursor = arcpy.UpdateCursor(lyr)
    for lnh in cursor:
        for col in fields:
            if col in places_by_col:
                if fields[col] == 'Integer' or fields[col] == 'Double' \
                   or fields[col] == 'SmallInteger':
                    value = lnh.getValue(col)
                
                    lnh.setValue(
                        col, 
                        round(value, int(places_by_col[col][PLACES_FIELD]))
                    )
                else:
                    continue
            else:
                print("{} not in {}".format(col, decimal_by_col_file))
        
        cursor.updateRow(lnh)
    
    del lyr
    
    return outputFile


def round_tables_values(fldTables, decimal_col_file, outFolder,
                        table_format='.shp'):
    """
    Round all column values using the number of decimal places written
    in a excel file in loop
    """
    
    import os
    from glass.pys.oss import lst_ff
    
    tables = lst_ff(fldTables, file_format=table_format)
    
    for table in tables:
        round_table_values(
            table, decimal_col_file, os.path.join(
                outFolder, 'rnd_' + os.path.basename(table)
            )
        )

