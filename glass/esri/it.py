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


"""
TIN TO RASTER
"""

def tin_to_raster(tin, cs, out, template=None, snap_rst=None):
    """
    TIN to Raster
    """
    if template:
        arcpy.env.extent = template
    
    if snap_rst:
        arcpy.env.snapRaster = snap_rst
    
    arcpy.ddd.TinRaster(
        tin, out, 
        data_type="FLOAT",
        method="LINEAR", 
        sample_distance=f"CELLSIZE {str(cs)}",
        z_factor="1"
    )
    
    if template:
        arcpy.env.extent = None
    
    if snap_rst:
        arcpy.env.snapRaster = None
    
    return out

