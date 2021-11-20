"""
Arcpy tools for information/data extraction
"""

import arcpy


def select_by_attr(inShp, sql, outShp):
    """
    Select data by attributes and write it to file
    """
    
    arcpy.Select_analysis(inShp, outShp, sql)
    
    return outShp


def select_by_attr_onview(inLyr, whereClause):
    """
    Select by attribute creating a new Table/Layer View (not writes a new file)
    """
    
    arcpy.SelectLayerByAttribute_management(
        inLyr, "NEW_SELECTION", whereClause
    )


def split_shp_by_two_attr(s, f1, f2, w):
    """
    Este script parte uma shpefile segundo a informacao disponivel em dois
    campos, ou seja, cada feature com a mesma combinacao de informacao
    relativa a dois campos e exportada para uma nova shapefile; estas
    combinacoes podem-se repetir em varias features 
    """
    
    from gesri.lyr import feat_lyr
    
    arcpy.env.workspace = w;
    lyr = feat_lyr(s)
    c = arcpy.SearchCursor(lyr); l = c.next(); dic = {}
    
    while l:
        f1v = l.getValue(f1)
        if f1v not in dic.keys():
            dic.update({l.getValue(f1): [l.getValue(f2)]})
        else:
            if l.getValue(f2) not in dic[f1v]:
                dic[f1v].append(l.getValue(f2))
        l = c.next()
    
    for v1 in dic.keys():
        for v2 in dic[v1]:
            """
            TODO: DECODE V1 AND V2 and DEL SPACES
            """
            nova_layer = '{f_1}_{v_1}_{f_2}_{v_2}.shp'.format(
                f_1=f1, f_2=f2, v_1=str(v1), v_2=str(v2)
            )
            
            """
            TODO: Define SQL based on the type of the fields f1 and f2
            """
            expressao = '{f_1}=\'{v_1}\' AND {f_2}=\'{v_2}\''.format(
                f_1=f1, f_2=f2, v_1=str(v1), v_2=str(v2)
            )
            
            arcpy.Select_analysis(lyr, nova_layer, expressao)


def split_shp_based_on_comparation(shp, f1, f2, inEpsg, outWork):
    """
    Split shp in two datasets:
    
    - shp_equal with the features with the same value in the attributes
    in f1 e f2;
    - shp_diff with the features with different values in the attributes
    in f1 e f2.
    f1 and f2 could be a string or a list 
    """
    
    import os
    from gesri.df.lyr import feat_lyr
    from gesri.df.prop.feat   import get_gtype
    from gesri.df.prop.fld    import lst_flds
    from gesri.df.mng.featcls import create_feat_class
    from gesri.df.mng.fld     import copy_fields
    
    f1 = [f1] if type(f1) == str else f1 if type(f1) == list else None
    
    f2 = [f2] if type(f2) == str else f2 if type(f2) == list else None
    
    if not f1 or not f2:
        raise ValueError('f1 and f2 values are not valid')
    
    if len(f1) != len(f2):
        raise ValueError('f1 and f2 should have the same length')
    
    arcpy.env.overwriteOutput = True
    
    # Create outputs
    inGeom = get_gtype(shp)
    equalShp = create_feat_class(
        os.path.join(outWork, '{}_equal{}'.format(
            os.path.splitext(os.path.basename(shp))[0],
            os.path.splitext(shp)[1]
        )),
        inGeom, inEpsg
    )
    equalLyr = feat_lyr(equalShp)
    
    difShp = create_feat_class(
        os.path.join(outWork, '{}_dif{}'.format(
            os.path.splitext(os.path.basename(shp))[0],
            os.path.splitext(shp)[1]
        )),
        inGeom, inEpsg
    )
    difLyr = feat_lyr(difShp)
    
    # Copy Fields
    inLyr = feat_lyr(shp)
    fields = lst_flds(inLyr)
    copy_fields(inLyr, equalLyr)
    copy_fields(inLyr, difLyr)
    
    # Read inputs and write in the outputs
    cursorRead  = arcpy.SearchCursor(inLyr)
    cursorEqual = arcpy.InsertCursor(equalLyr)
    cursorDif   = arcpy.InsertCursor(difLyr)
    
    line = cursorRead.next()
    while line:
        val_1 = [line.getValue(f) for f in f1]
        val_2 = [line.getValue(f) for f in f2]
        
        if val_1 == val_2:
            new_row = cursorEqual.newRow()
        
        else:
            new_row = cursorDif.newRow()
        
        new_row.Shape = line.Shape
        
        for field in fields:
            if field == 'FID' or field == 'Shape' or field == 'ID':
                continue
            
            new_row.setValue(field, line.getValue(field))
        
        if val_1 == val_2:
            cursorEqual.insertRow(new_row)
        
        else:
            cursorDif.insertRow(new_row)
            
        line = cursorRead.next()


def clip_by_feature(inputFeatures, clipFeatures, folderOutputs, base_name,
                    clip_feat_id='FID'):
    """
    Clip inputFeatures for each feature in the clipFeatures layer
    Store all produced layers in the folderOutputs.
    """
    
    import os
    from glass.pys.oss import create_folder
    from gesri.df.lyr  import feat_lyr
    from glass.cpu.arcg.mng.fld import type_fields
    
    # ########### #
    # Environment #
    # ########### #
    arcpy.env.overwriteOutput = True
    
    # ################ #
    # Now, is for real #
    # ################ #
    inputLyr = feat_lyr(inputFeatures)
    clipLyr  = feat_lyr( clipFeatures)
    
    if not os.path.exists(folderOutputs):
        create_folder(folderOutputs)
    
    wTmp = create_folder(os.path.join(folderOutputs, 'tmp_clip'))
    
    # Get id's field type
    fld_type = type_fields(clipLyr, field=str(clip_feat_id))
    
    expression = '{fld}=\'{_id}\'' if str(fld_type) == 'String' else \
        '{fld}={_id}'
    
    c = arcpy.SearchCursor(clipLyr)
    l = c.next()
    while l:
        fid = str(l.getValue(clip_feat_id))
        
        selection = select_by_attr(
            clipLyr,
            expression.format(fld=clip_feat_id, _id=fid),
            os.path.join(wTmp, 'clp_{}.shp'.format(fid))
        )
        
        clip_f = clip(
            inputLyr, selection,
            os.path.join(folderOutputs, '{}_{}.shp'.format(base_name, fid))
        )
        
        l = c.next()

