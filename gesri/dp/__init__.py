"""
Copy data
"""

import arcpy

def copy_feat(inshp, outshp):
    """
    Copy features
    """

    arcpy.CopyFeatures_management(inshp, outshp)

    return outshp


def merge(lst, outShp):
    """
    Merge Feature Classes into one
    """
    
    arcpy.Merge_management(';'.join(lst), outShp)
    
    return outShp


def append(inShp, targetShp):
    """
    Append inShp into targetShp
    """
    
    arcpy.Append_management(
        inShp, targetShp, "NO_TEST", "", ""
    )


def delete(__file):
    arcpy.Delete_management(__file)


def del_empty_files(folder, file_format):
    """
    List all feature classes in a folder and del the files with
    0 features
    """
    
    from glass.pys.oss  import lst_ff
    from glass.prop.feat import feat_count
    
    fc = lst_ff(folder, file_format=file_format)
    
    for shp in fc:
        feat_number = feat_count(shp, gisApi='arcpy')
        
        if not feat_number:
            delete(shp)

