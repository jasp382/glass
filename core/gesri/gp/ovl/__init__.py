"""
Overlay tools
"""

import arcpy


def clip(inputFeatures, clipFeatures, outFeatures):
    """
    Execute Clip Tool
    """
    
    arcpy.Clip_analysis(inputFeatures, clipFeatures, outFeatures)
    
    return outFeatures


def clip_by_featcls(inShp, clipFolder, folderOutputs, fFormat='.shp'):
    """
    Clip inShp using each feature class in the clipFolder as
    clip features.
    """
    
    import os
    from glass.pys.oss import lst_ff, fprop
    
    clip_fc = lst_ff(clipFolder, file_format=fFormat)
    
    for fc in clip_fc:
        clip(inShp, fc, os.path.join(
            folderOutputs, '{}_{}'.format(
                fprop(inShp, 'fn'), os.path.basename(fc)
            )
        ))


def intersect(lst_lyr, outShp):
    arcpy.Intersect_analysis(lst_lyr, outShp)
    return outShp


def folderShp_Intersection(inFolder, intFeatures, outFolder):
    """
    Intersect all feature classes in a folder with the feature classes
    listed in the argument intFeatures (path to the file).
    """
    
    import os
    from glass.pys.oss import create_folder
    from gesri.df.lyr  import feat_lyr
    
    # Environment
    arcpy.env.overwriteOutput = True
    # Workspace
    arcpy.env.workspace = inFolder
    
    if type(intFeatures) != list:
        intFeatures = [intFeatures]
    
    if not os.path.exists(outFolder):
        create_folder(outFolder)
    
    # List feature classes in inFolder
    fc_infld = arcpy.ListFeatureClasses()
    
    # Create Layer objects
    lyr_infld = [feat_lyr(os.path.join(inFolder, str(fc))) for fc in fc_infld]
    lyr_intFeat = [feat_lyr(fc) for fc in intFeatures]
    
    # Intersect things
    for i in range(len(lyr_infld)):
        intersect(
            [lyr_infld[i]] + lyr_intFeat,
            os.path.join(outFolder, os.path.basename(str(fc_infld[i])))
        )


def union(lyrA, lyrB, outShp):
    """
    Calculates the geometric union of the overlayed polygon layers, i.e.
    the intersection plus the symmetrical difference of layers A and B.
    """
    
    import arcpy
        
    if type(lyrB) == list:
        lst = [lyrA] + lyrB
    else:
        lst = [lyrA, lyrB]
        
    arcpy.Union_analysis(";".join(lst), outShp, "ALL", "", "GAPS")
    
    return outShp


def erase(inShp, erase_feat, out):
    """
    Difference between two feature classes
    """
    
    import arcpy
        
    arcpy.Erase_analysis(
        in_features=inShp, erase_features=erase_feat, 
        out_feature_class=out
    )
    
    return out

