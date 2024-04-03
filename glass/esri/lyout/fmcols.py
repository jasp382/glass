"""
Real methods to produce maps layouts
"""

import arcpy


def col_to_map_v1(main_mxd, lyrs_to_change, layout_elm_file, symbology_to_apply,
              outDir, exportMap=None, maps_format='.jpg'):
    """
    TODO: ADD A MORE DETAILED DESCRIPTION
    
    Create a map for every column in a layer - Useful if you want
    to mantain layers symbology (colors) and inverval breaks.
    
    * main_mxd = path to a mxd template (all maps produced will be like
    this template);
    
    * lyrs_to_change = name of the layers to be changed from map to map;
    
    * layout_elm_file = file with the indication of what text should appear
    in each text element of the layout when some column is used as value
    field;
    eg.,
    
                    | id_element_1 | ... | id_element_n
    col_value_name1 |  some_text   | ... |  some_text
    col_value_name2 |  some_text   | ... |  some_text
    
    -> The goal is to mantain classes values and number of classes and colors
     - change only value field.
    
    NOT WORKING DO A ARCGIS BUG:
    When changing value field, symbology is automaticaly reseted.
    See col_to_map_v2 to a work around!
    Another work around could be the utilization of a custom ramp color
    """
    
    import os
    from glass.pys                import obj_to_lst
    from glass.dct                import tbl_to_obj
    from gesri.maps.arctbx.fields import list_fields
    from gesri.maps.arctbx.lyrs   import lst_layers
    from gesri.maps.arctbx.graph  import get_elem_by_name
    from gesri.maps.arctbx.wmap   import mxd_saveas
    
    if exportMap:
        from gesri.arcg.maps.wmap import write_map
    
    # List Cols to be maped and graphic elements to be changed
    cols_and_elements = tbl_to_obj(
        layout_elm_file, useFirstColAsIndex=True, output='dict'
    )
    
    # Prepare list of layers to modify
    lyrs_to_change = obj_to_lst(lyrs_to_change)
    
    if not lyrs_to_change: raise ValueError(
        'lyrs_to_change should by of type str, unicode or list'
    )
    
    # Open mxd and change it
    mxd = arcpy.mapping.MapDocument(main_mxd)
    
    # List layers objects to be modified on mxd
    lyr_objs = lst_layers(mxd, lyrNames=lyrs_to_change, storeDfs=True)
    lyr_objs = [lyr_objs] if type(lyr_objs) != list else lyr_objs
    
    if not len(lyr_objs):
        raise ValueError(
            'Cannot find any layer to be changed in the given mxd project'
        )
    
    # Get Text elements in mxd to be changed
    elem_names = cols_and_elements[cols_and_elements.keys()[0]].keys()
    text_elem  = get_elem_by_name(mxd, elem_names)
    
    if not text_elem:
        raise ValueError(
            'No Graphic/Text element was finded'
        )
    
    # For every column, export a new map
    for col in cols_and_elements:
        # Change layer value field and symbology
        for lyr in lyr_objs:
            # TODO: Add more symbology type
            if lyr[1].symbologyType == "GRADUATED_COLORS":
                if col in list_fields(lyr[1]):
                    lyr[1].symbology.valueField = col
                
                else:
                    print(f'{col} is not in the layer {str(lyr[1].name)}')
            
            else:
                print(
                    f'Symbology type of layer {str(lyr[1].name)} cannot be processed '
                    'by this script.'
                )
        
        # Change every text elements
        for elm_name in text_elem:
            text_elem[elm_name].text = cols_and_elements[col][elm_name]
        
        if exportMap:
            outmap = write_map(mxd, os.path.join(outDir, col + maps_format))
        
        # Create new mxd
        mxd_saveas(mxd, col + '.mxd')


def col_to_map(main_mxd, lyrs_sourcedata, joker_field, layout_elm_file,
               mapsDir, mxdDir=None, maps_format='.jpg', includeMxdNameInMap=None):
    """
    TODO: ADD A MORE DETAILED DESCRIPTION
    
    WORK AROUND for col_to_map_v1
    if we change the valueField, the symbology will be reseted. So, lets
    change the values of the valueField
    
    GOAL: Create a map for every column in a layer - Use if you want
    to mantain layers symbology including colors and inverval breaks.
    
    * main_mxd = path to a mxd template (all maps produced will be like
    this template);
    
    * lyrs_sourcedata = path to the data source of the layers
    that will be changed from map to map;
    
    * joker_field = name of the field that will store the values to be
    mapped (same field but different values);
    
    * layout_elm_file = file with the indication of what text should appear
    in each text element of the layout when some column is used as value
    field;
    eg.,
    
                    | id_element_1 | ... | id_element_n
    col_value_name1 |  some_text   | ... |  some_text
    col_value_name2 |  some_text   | ... |  some_text
    
    -> The goal is to mantain classes values and number of classes and colors
     - change only value field.
    """
    
    import os
    from glass.rd               import tbl_to_obj
    from glass.cpu.arcg.mng.fld  import calc_fld
    from glass.esri.lyout.tbx.graph import get_elem_by_name
    from glass.esri.lyout.tbx.wmap  import mxd_saveas
    from glass.esri.lyout.tbx.wmap  import write_map
    
    if includeMxdNameInMap:
        from glass.pys.oss import fprop
        mapBaseName = fprop(main_mxd, forceLower=True) + "_"
    
    else:
        mapBaseName = ""
    
    maps_format = '.' + maps_format if maps_format[0] != '.' else maps_format
    
    # List Cols to be maped and graphic elements to be changed
    cols_and_elements = tbl_to_obj(
        layout_elm_file, useFirstColAsIndex=True, output='dict'
    )
    
    for col in cols_and_elements:
        print(f"Producing {col} Map")
        # Update JOKER FIELD
        calc_fld(
            lyrs_sourcedata, joker_field, f"[{str(col)}]"
        )
        
        # Open mxd and change it
        mxd = arcpy.mapping.MapDocument(main_mxd)
        
        # Get Text elements in the main mxd to be changed
        elem_names = cols_and_elements[cols_and_elements.keys()[0]].keys()
        text_elem  = get_elem_by_name(mxd, elem_names)
        
        if not text_elem:
            print('No Graphic/Text element was finded')
        
        # Change every text elements
        for elm_name in text_elem:
            text_elem[elm_name].text = cols_and_elements[col][elm_name]
        
        outmap = write_map(mxd, os.path.join(
            mapsDir, f"{mapBaseName}{col}{maps_format}"
        ))
        
        # Create a new mxd
        if mxdDir:
            mxd_saveas(os.path.join(mxdDir, f"{mapBaseName}{col}.mxd"))
        
        # Close mxd
        del mxd
        
        print(f"{col} Map is done!")


def col_to_map_mlyr(main_mxd, lyrs_src, lyrs_joker, mapColsTbl, graphicsTbl,
                    out_maps, mapsFormat='.jpg', out_mxd=None):
    """
    Same as col_to_map, but this one allows multiple layers chaging
    
    lyrs_src = {
        "lyr1_name" : r'/path/to/datasource.shp',
        "lyr2_name" : r'/path/to/datasource.shp'
        ...
    }
    
    lyrs_joker = {
        "lyr1_name" : "joker_field_name",
        "lyr2_name" : "joker_field_name"
    }
    
    mapColsTbl = path to table with the relation between columns and map
                | lyr_1_name | ... | lyr_n_name 
     map_alias1 |  col_name  | ... |  col_name
     map_alias2 |  col_name  | ... |  col_name
     
    graphicsTbl = path to table with relation between maps and values to assign
    to graphic elements
                | element_1 | ... | element_n
     map_alias1 | some_text | ... | some_text
     map_alias2 | some_text | ... | some_text
    """
    
    import os
    from glass.rd                   import tbl_to_obj
    from glass.esri.tbl.col         import cols_calc
    from glass.esri.lyout.tbx.graph import get_elem_by_name
    from glass.esri.lyout.tbx.wmap  import mxd_saveas, write_map
    
    mapsFormat = mapsFormat if mapsFormat[0] == '.' else '.' + mapsFormat
    
    # Get maps to do
    mapsToDo = tbl_to_obj(
        mapColsTbl, useFirstColAsIndex=True, output='dict'
    )
    
    # Get dict with association between maps and graphics elements
    graphicElem = tbl_to_obj(
        graphicsTbl, useFirstColAsIndex=True, output='dict'
    )
    
    # Create new maps
    for newMap in mapsToDo:
        print(f"Producing {newMap} Map")
        
        # Update JOKER's FIELD's
        for lyr in mapsToDo[newMap]:
            cols_calc(
                lyrs_src[lyr], lyrs_joker[lyr],
                f"[{str(mapsToDo[newMap][lyr])}]"
            )
        
        # Open mxd and change it
        mxd = arcpy.mapping.MapDocument(main_mxd)
        
        # Get Text elements in the main mxd to be changed
        elem_names = graphicElem[newMap].keys()
        text_elem  = get_elem_by_name(mxd, elem_names)
        
        if not text_elem:
            print('No Graphic/Text element was finded')
        
        for e in text_elem:
            text_elem[e].text = graphicElem[newMap][e]
        
        outmap = write_map(mxd, os.path.join(out_maps, newMap + mapsFormat))
        
        # Create a new mxd only because
        if out_mxd:
            mxd_saveas(mxd, os.path.join(out_mxd, newMap + '.mxd'))
        
        # Close mxd
        del mxd
        
        print(f"{newMap} Map is done!")


def col_to_map_equalIntervals(main_mxd, lyrs_to_change,
        layout_elm_file, prefix_interval_label, outMaps,
        saveMxd=None, nr_intervals=7, min_max_file=None,
        intervals_file=None, maps_format='.jpg', intLabelSingle=True):
    """
    TODO: ADD A MORE PROPER DESCRIPTION
    
    Create a map for every column in a layer - Use if you want to mantain
    layers colors and change the interval breaks.
    
    * main_mxd = path to a mxd template (all maps produced will be like
    this template);
    
    * lyrs_to_change = name of the layers to be changed from map to map
    (should be the same layer but with different names);
    
    * layout_elm_file = file with the indication of what text should appear
    in each text element of the layout when some column is used as value
    field;
    eg.,
    
                    | id_element_1 | ... | id_element_n
    col_value_name1 |  some_text   | ... |  some_text
    col_value_name2 |  some_text   | ... |  some_text
    
    * prefix_interval_label = label classes elements name prefix
    (label elements should be like this 'legend_1;legend_2');
    
    * min_max_file = file with the indication of the minimum and maximum
    values to consider when calculating the intervals for each column
    eg.,
                    | min | max
    col_value_name1 |  x  |  y
    col_value_name2 |  x  |  y
    
    * intervals_file = file with the intervals
    
    You can not use min_max_file and intervals_file at the
    same time
    
    -> Change only intervals values and labels in the legend.
    New intervals that will be used will be calculated using
    equal interval method.
    
    Note: Legend graphic elements must be ungrouped.
    """
    
    import os
    
    from glass.pys                   import obj_to_lst
    from glass.rd                    import tbl_to_obj
    from glass.esri.lyout.tbx.fields import list_fields
    from glass.esri.lyout.tbx.graph  import get_elem_by_name, get_elem_by_prefix
    from glass.esri.lyout.tbx.lyrs   import lst_layers
    from glass.esri.lyout.tbx.wmap   import mxd_saveas, write_map
    from glass.esri.tbl.col          import get_equal_int
    from glass.cls.dbreaks           import _get_equal_int_
    
    if min_max_file and intervals_file:
        raise ValueError(
            'min_max_file and intervals_file are not allowed together'
        )
    
    maps_format = maps_format if maps_format[0] == '.' else '.' + maps_format
    
    # List Cols to be maped and graphic elements to be changed
    cols_and_elements = tbl_to_obj(
        layout_elm_file, useFirstColAsIndex=True, output='dict'
    )
    
    # Prepare list of layers to modify
    lyrs_to_change = obj_to_lst(lyrs_to_change)
    
    if not lyrs_to_change: raise ValueError(
        'lyrs_to_change should by of type str, unicode or list'
    )
    
    # Open mxd and change it
    mxd = arcpy.mapping.MapDocument(main_mxd)
    
    # List layers objects to be modified from mxd
    lyr_objs = lst_layers(mxd, lyrNames=lyrs_to_change, storeDfs=True)
    lyr_objs = [lyr_objs] if type(lyr_objs) != list else lyr_objs
    
    if not len(lyr_objs):
        raise ValueError(
            'Cannot find any layer to be changed in the given mxd project'
        )
    
    # Get Text elements in mxd to be changed
    elem_names = cols_and_elements[cols_and_elements.keys()[0]].keys()
    text_elem = get_elem_by_name(mxd, elem_names)
    
    if not text_elem:
        raise ValueError(
            'We can not find any text element with names given'
        )
    
    # Get text elements from the map legend
    leg_elements = get_elem_by_prefix(mxd, prefix_interval_label)
    leg_elm = {e.name: e for e in leg_elements}
    del leg_elements
    leg_elm_names = leg_elm.keys()
    leg_elm_names.sort()
    
    # There is a file with the indication of minimum and max values to be
    # used?
    col_min_max = tbl_to_obj(
        min_max_file, useFirstColAsIndex=True, output='dict'
    ) if min_max_file else None
    
    # There is a file with the intevals to be used?
    intervals_dict = tbl_to_obj(
        intervals_file, useFirstColAsIndex=True, output='dict'
    ) if intervals_file else None
    
    # For every column, export a new map
    for col in cols_and_elements:
        print(f"Producing {col} Map")
        # Change layer value field and adjust intervals
        if intervals_dict:
            int_breaks = [
                intervals_dict[col][i] for i in range(nr_intervals+1)]
        else:
            int_breaks = get_equal_int(
                lyr_objs[0][1].dataSource, col, nr_intervals
            ) if not col_min_max else _get_equal_int_(
                col_min_max[col]['max'], col_min_max[col]['min'],
                nr_intervals
            )
        
        if not intLabelSingle:
            breaks_label = [
                f"{int_breaks[i-1]} - {int_breaks[i]}"
                for i in range(1, len(int_breaks))
            ]
            
        else:
            breaks_label = [str(i) for i in int_breaks]
        
        for lyr in lyr_objs:
            # TODO: Add more symbology types
            if lyr[1].symbologyType == "GRADUATED_COLORS":
                if col in list_fields(lyr[1]):
                    lyr[1].symbology.valueField = col
                    lyr[1].symbology.classBreakValues = int_breaks
                
                else:
                    print(f'{col} is not in the layer {str(lyr[1].name)}')
            
            else:
                print(
                    f'Symbology type of layer {str(lyr[1].name)} cannot be processed '
                    'by this script.'
                )
        
        # Change every text elements
        #print intervals_dict
        #print leg_elm_names
        for elm_name in text_elem:
            text_elem[elm_name].text = cols_and_elements[col][elm_name]
        
        # Change intervals labels in the legend
        for i in range(len(leg_elm_names)):
            # TODO: here we have a problem
            # Round values are used in labeling but not in the classification
            # Think about that
            leg_elm[leg_elm_names[i]].text = breaks_label[i]
        
        
        outmap = write_map(mxd, os.path.join(outMaps, col + maps_format))
        
        # Create a new mxd
        if saveMxd:
            mxd_saveas(mxd, os.path.join(saveMxd, col + '.mxd'))
        
        print(f"{col} Map is done!")

