"""
Do things with BGRI from INE
"""

def assign_units_to_polygons(bgri, polygons, id_bgri, id_polygon,
                             field_bgri='pol_assigned', workspace=None):
    """
    Permite verificar a que municipio ou area de influencia uma subsecao
    estatistica pertence (territorialmente).
    
    Se uma subseccao se intersectar com mais de um poligono, a primeira fica
    relacionada ao poligono que ocupa maior parte da sua area (isto pode 
    levantar algumas questoes, mas para ja fica assim).
    
    A relacao entre a subsecao e o poligono que com ela intersecta ficara 
    escrita num novo campo da bgri
    
    Use Arcgis to accomplish this
    """
    
    import arcpy;            import os
    from gesri.lyr        import feat_lyr
    from gesri.anls.ovlay import intersect
    from gesri.mng.fld    import add_field
    from gesri.prop.fld   import get_geom_field
    from gesri.prop.feat  import get_feat_area
    
    arcpy.env.overwriteOutput = True
    workspace = workspace if workspace else os.path.dirname(bgri)
    
    # Create feature layers of the inputs
    bgriLyr, polygLyr = [feat_lyr(bgri), feature_lyr(polygons)]
    
    # Intersect
    int_fc = os.path.join(workspace, 'bgri_and_polygons.shp')
    int_fc = intersect([bgriLyr, polygLyr], int_fc)
    
    # Relate bgri unit with polygon entities
    intLyr = feat_lyr(int_fc)
    
    cursor = arcpy.SearchCursor(intLyr)
    bgri_polygons = {}
    geomField = get_geom_field(intLyr)
    for linha in cursor:
        fid_bgri = linha.getValue(id_bgri)
        fid_polygon = linha.getValue(id_polygon)
        
        area = get_feat_area(linha, geomField)
        
        if fid_bgri not in bgri_polygons.keys():
            bgri_polygons[fid_bgri] = [fid_polygon, area]
        
        else:
            if area > bgri_polygons[fid_bgri][1]:
                bgri_polygons[fid_bgri] = [fid_polygon, area]
            
            else:
                continue
    
    # Write output
    del cursor, linha
    
    add_field(bgriLyr, field_bgri, "TEXT", "15")
    
    cursor = arcpy.UpdateCursor(bgriLyr)
    for linha in cursor:
        fid_bgri = linha.getValue(id_bgri)
        linha.setValue(field_bgri, bgri_polygons[fid_bgri][0])
        cursor.updateRow(linha)
    
    del cursor, linha, bgriLyr, polygLyr

