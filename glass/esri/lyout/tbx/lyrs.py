"""
Mapping operations layer
"""

import arcpy


def lst_layers(__mxd, dataFrames=None, lyrNames=None, storeDfs=None):
    """
    List layers objects in mxd
    """
    
    from glass.pys import obj_to_lst
    
    lyrNames   = obj_to_lst(lyrNames)
    dataFrames = obj_to_lst(dataFrames)
    
    dfs = arcpy.mapping.ListDataFrames(__mxd)
    
    __lyr = []
    for df in dfs:
        if dataFrames:
            if str(df.name) not in dataFrames:
                continue
        
        lyr = arcpy.mapping.ListLayers(__mxd, data_frame=df)
        
        if lyrNames:
            lyr = [i for i in lyr if i.name in lyrNames]
        
        if storeDfs:
            lyr = [(df, i) for i in lyr]
        
        __lyr += lyr
    
    if len(__lyr) == 0:
        return None
    
    elif len(__lyr) == 1:
        return __lyr[0]
    
    else:
        return __lyr


def get_layers_by_dataframe(mxdObj):
    """
    Return {
        df_name : {
            lyr_name : lyr_obj
        },
        ...
    }
    """
    
    dfs = arcpy.mapping.ListDataFrames(mxdObj)
    
    dicDf = {}
    for df in dfs:
        lyrInDf = arcpy.mapping.ListLayers(mxdObj, data_frame=df)
        
        lyrs = {x.name : x for x in lyrInDf}
        
        dicDf[df.name] = lyrs
    
    return dicDf


def save_layer_file(inLyr, outLyrPath):
    """
    Save the symbology of a layer into a layer file
    """
    
    arcpy.SaveToLayerFile_management(
        inLyr, outLyrPath, "ABSOLUTE"
    )
    
    return outLyrPath

