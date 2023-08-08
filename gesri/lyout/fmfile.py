"""
Mass production of ArcGIS layouts
"""

import arcpy

def files_to_map(main_mxd, lyr_to_change, dataFrame, lyr_folder,
                 layout_elm_table, outDir, exportMap=None,
                 lyr_extent_name=None, maps_format='.jpg',
                 extentTolerance=200):
    """
    Create a map for every file in a folder
    
    Only works for Feature Classes
    
    * main_mxd = path to a mxd template (all maps produced will be like
    this template);
    
    * lyr_to_change is a table as:
       | lyr_1_name | ... | lyr_n_name 
     0 | some_name  | ... | some_name
     1 | some_name  | ... | some_name
     
    * lyr_folder = {
        lyr_1_name : '/path/to/files/to/be/used/as/lyr_1_name',
        lyr_2_name : '/path/to/files/to/be/used/as/lyr_2_name'
    
    * layout_elm_table = file with the indication of what text should appear
    in each text element of the layout when some column is used as value
    field;
    
                   | id_element_1 | ... | id_element_n
    file_lyr_name1 |  some_text   | ... |  some_text
    file_lyr_name2 |  some_text   | ... |  some_text
    """
    
    import os
    from glass.pys.oss           import lst_ff
    from glass.dct                 import tbl_to_obj
    from glass.maps.arctbx.lyrs   import lst_layers
    from glass.maps.arctbx.dframe import lst_dataframe
    from glass.maps.arctbx.graph  import get_elem_by_name
    from glass.maps.arctbx.wmap   import mxd_saveas
    from glass.maps.arctbx.wmap   import write_map
    
    # Prepare global variables
    mxdDir  = outDir
    mapsDir = exportMap if os.path.isdir(exportMap) else outDir
    
    # List files to be used in each map by layer name
    filesByLyr = tbl_to_obj(
        lyr_to_change, useFirstColAsIndex=True, output='dict'
    )
    
    # List graphic elements to be changed
    files_and_element = tbl_to_obj(
        layout_elm_table, useFirstColAsIndex=True, output='dict'
    )
    
    # Produce maps
    for __map in filesByLyr:
        print "Producing {} Map".format(str(__map))
        
        # Open mxd and change it
        mxd = arcpy.mapping.MapDocument(main_mxd)
        
        # Get Text elements in the main mxd to be changed
        elem_names = files_and_element[files_and_element.keys()[0]].keys()
        text_elem  = get_elem_by_name(mxd, elem_names)
        
        if not text_elem:
            print 'No Graphic/Text element was finded'
        
        # Change every text elements
        for elem_name in text_elem:
            text_elem[elem_name].text = files_and_element[__map][elem_name]
        
        # Change layer datasource
        lyrs = lst_layers(mxd, lyrNames=filesByLyr[__map].keys())
        
        df = lst_dataframe(mxd, dfNames=dataFrame)
        
        for lyr in lyrs:
            lyr.replaceDataSource(
                lyr_folder[str(lyr.name)],
                "NONE",
                filesByLyr[__map][str(lyr.name)],
                True
            )
        
        # Set new map extension
        if not lyr_extent_name:
            lyr_extent_name = str(lyrs[0].name)
        
        for lyr in lyrs:
            if str(lyr.name) != lyr_extent_name:
                continue
            else:
                ext = lyr.getExtent()
                
                newExtent = df.extent
                newExtent.XMin = ext.XMin - extentTolerance
                newExtent.YMin = ext.YMin - extentTolerance
                newExtent.XMax = ext.XMax + extentTolerance
                newExtent.YMax = ext.YMax + extentTolerance
                
                df.extent = newExtent
        
        outmap = write_map(
            mxd, os.path.join(mapsDir, 'map_{}{}'.format(
                str(__map), maps_format
            ))
        )
        
        # Create a new mxd
        mxd_saveas(mxd, os.path.join(mxdDir, 'map_{}.mxd'.format(str(__map))))
        
        # Close mxd
        del mxd
        
        print "Map {} is done!".format(str(__map))


def maps_by_extent(extentSource, baseMxd, MAIN_DATAFRAME, EXTENT_LYR_NAME,
                   CONTEXT_DATAFRAME, MAP_GRAPH_ELEM, outputMxd,
                   outputMaps=None, mapsFormat='.pdf'):
    """
    Export a new map for each "Extent".
    
    Extent is a bounding box file
    
    * extentSource - path to the folder with the bounding boxes files.
    A new map will be generated for every file in this folder.
    
    * baseMxd - path to an template MXD file. The new maps will have the same
    structure.
    
    * MAIN_DATAFRAME - name of the dataframe in the baseMxd that will have
    it extent changed from map to map.
    
    * EXTENT_LYR_NAME - name of the layer that will have it extent changed
    from map to map.
    
    * CONTEXT_DATAFRAME - dict with metainfo about other dataframe with
    data about the geographic context.
    E.g.
    CONTEXT_DATAFRAME = {
        "zoom_pt" : {
            "PATHDATA" : r'D:\TRENMO_JASP\SITIOS_FATIMA\acf_versao_final\lmt_conc',
            "LAYERS" : {
                # LAYER NAME : FIELD IN EXTENT_LAYER WITH THE NAME OF THE FILE
                # THAT SOULD BE USED IN THE LAYER WITH KEY NAME
                "ref_concelho" : "concelho"
            }
        },
        "zoom_concelho" : {
            "PATHDATA" : r'D:\TRENMO_JASP\SITIOS_FATIMA\acf_versao_final\lmt_conc',
            "LAYERS" : {
                "ref_concelho" : "concelho",
                "ref_grid" : "EXTENTFILE"
            },
            "ISZOOM" : "ref_concelho",
            "EXTENT_TOLERANCE" : 1000
        }
    }
    
    MAP_GRAPH_ELEM - file with the indication of what text should appear
    in each text element of the layout when some file is used as data source
    of the EXTENT_LYR;
    
                   | id_element_1 | ... | id_element_n
    file_lyr_name1 |  some_text   | ... |  some_text
    file_lyr_name2 |  some_text   | ... |  some_text
    """
    
    import os
    from glass.dct                import tbl_to_obj
    from glass.pys.oss            import get_filename
    from glass.cpu.arcg.mng.fld   import list_fields
    from glass.maps.arctbx.lyrs   import lst_layers
    from glass.maps.arctbx.lyrs   import get_layers_by_dataframe
    from glass.maps.arctbx.dframe import lst_dataframe
    from glass.maps.arctbx.graph  import get_elem_by_name
    from glass.maps.arctbx.wmap   import write_map
    from glass.maps.arctbx.wmap   import mxd_saveas
    
    outputMaps = outputMxd if not os.path.isdir(outputMaps) else outputMaps
    mapsFormat = mapsFormat if mapsFormat[0] == '.' else '.' + mapsFormat
    
    # List extent files
    arcpy.env.workspace = extentSource
    maps_ext = arcpy.ListFeatureClasses()
    
    attrs_data = {}
    for extFile in maps_ext:
        cursor = arcpy.SearchCursor(os.path.join(extentSource, extFile))
        
        lnh = cursor.next()
        
        fields = list_fields(os.path.join(extentSource, extFile))
        
        c = 0
        while lnh:
            if c:
                break
            
            fdata = {
                field : lnh.getValue(
                    field
                ) for field in fields if field != 'Shape' and \
                    field != "FID" and field != "Id"
            }
            
            c += 1
            lnh = cursor.next()
        
        attrs_data[extFile] = fdata
    
    # List graphic elements to be changed
    files_and_element = tbl_to_obj(
        MAP_GRAPH_ELEM, useFirstColAsIndex=True, output='dict'
    )
    
    """
    For each extent file, open the main mxd and change extent
    of the main dataframe and change some layers in contextual dataframes
    """
    for extFile in maps_ext:
        # Open mxd
        mxd = arcpy.mapping.MapDocument(baseMxd)
        
        # Get Text elements in the main mxd to be changed
        elem_names = files_and_element[files_and_element.keys()[0]].keys()
        text_elem = get_elem_by_name(mxd, elem_names)
        
        if not text_elem:
            print 'No Graphic/Text element was finded'
        
        # Change every text elements
        for elem_name in text_elem:
            text_elem[elem_name].text = files_and_element[
                os.path.splitext(extFile)[0]][elem_name]
        
        # Set new map extension
        refDf  = lst_dataframe(mxd, dfNames=[MAIN_DATAFRAME])
        refLyr = lst_layers_by_name(
            mxd, dataFrames=MAIN_DATAFRAME, lyrNames=EXTENT_LYR_NAME
        )
        
        refLyr.replaceDataSource(
            extentSource, "NONE", os.path.splitext(extFile)[0], True
        )
        
        ext = refLyr.getExtent()
        
        newExtent = refDf.extent
        newExtent.XMin, newExtent.YMin = ext.XMin, ext.YMin
        newExtent.XMax, newExtent.YMax = ext.XMax, ext.YMax
        
        refDf.extent = newExtent
        
        # Change Context Dataframes
        lyrByDf = get_layers_by_dataframe(mxd)
        for df in CONTEXT_DATAFRAME:
            for mlyr in CONTEXT_DATAFRAME[df]["LAYERS"]:
                if CONTEXT_DATAFRAME[df]["LAYERS"][mlyr] != "EXTENTFILE":
                    mlyrsrc = os.path.join(
                        CONTEXT_DATAFRAME[df]["PATHDATA"],
                        attrs_data[extFile][CONTEXT_DATAFRAME[df]["LAYERS"][mlyr]]
                    )
                else:
                    mlyrsrc = os.path.join(extentSource, extFile)
                
                lyrByDf[df][mlyr].replaceDataSource(
                    os.path.dirname(mlyrsrc), "NONE",
                    os.path.splitext(os.path.basename(mlyrsrc))[0], True
                )
                
                if "ISZOOM" in CONTEXT_DATAFRAME[df]:
                    if mlyr == CONTEXT_DATAFRAME[df]["ISZOOM"]:
                        cdf  = list_dataframe_by_name(mxd, [df])[0]
                        
                        if "EXTENT_TOLERANCE" in CONTEXT_DATAFRAME[df]:
                            extTol = CONTEXT_DATAFRAME[df]["EXTENT_TOLERANCE"]
                        else:
                            extTol = 0
                        
                        lext = lyrByDf[df][mlyr].getExtent()
                        nExt = cdf.extent
                        nExt.XMin = lext.XMin - extTol
                        nExt.YMin = lext.YMin - extTol
                        nExt.XMax = lext.XMax + extTol
                        nExt.YMax = lext.YMax + extTol
                        
                        cdf.extent = nExt
        
        # Create a new mxd and export map
        outmap = write_map(
            mxd, os.path.join(outputMaps, get_filename(extFile) + mapsFormat)
        )
        
        mxd_saveas(os.path.join(
            outputMxd, '{}.mxd'.format(get_filename(extFile))
        ))
        
        del mxd

