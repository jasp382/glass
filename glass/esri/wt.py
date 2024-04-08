"""
Data to File using arcpy
"""

import arcpy

def tbl_to_tbl(inTable, outTable):
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



def obj_to_rst(obj, out, lower_left, cellsize, ndval):
    """
    Write Numpy Array in File
    """


    nrst = arcpy.NumPyArrayToRaster(
        obj, lower_left, cellsize,
        value_to_nodata=ndval
    )

    nrst.save(out)

    return out

