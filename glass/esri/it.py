"""
Interoperability
"""

import arcpy

def table_to_table(inTable, outTable):
    """
    Record table in a file
    Useful when we are using Network Analyst
    """
    
    import os
    
    arcpy.TableToTable_conversion(
        in_rows=inTable,
        out_path=os.path.dirname(outTable),
        out_name=os.path.basename(outTable), 
        where_clause="", 
        field_mapping="", 
        config_keyword=""
    )
    
    return outTable


def featurecls_to_featurecls(inShp, outShp):
    """
    Record feature layer in a file
    Useful when we are using Network Analyst
    """
    
    import os
    
    arcpy.FeatureClassToShapefile_conversion(
        Input_Features=inShp,
        Output_Folder=outShp
    )

