"""
Automatic Layouts production
"""

def layoutv1(mxd, geodata, mapstbl, lyt_template,
    map_template, lyrint, outmaps):
    """
    Layout V1

    muda apenas layer com valores quantitativos
    agrupados em intervalos de valores
    """

    import arcpy, pprint
    import os
    from glass.ng.rd import tbl_to_obj

    mapstodo = tbl_to_obj(mapstbl)

    mapsattr = list(mapstodo.columns.values)

    aprx = arcpy.mp.ArcGISProject(mxd)

    # Get map
    mapobj = aprx.listMaps(map_template)[0]
    lyr = mapobj.listLayers(lyrint)[0]

    for i, r in mapstodo.iterrows():
        current_dict = lyr.connectionProperties

        replace_dict = {
            'connection_info' : {'database' : geodata},
            'dataset' : '{}.shp'.format(r.slug),
            'workspace_factory' : 'Shape File'
        }

        lyr.updateConnectionProperties(current_dict, replace_dict)

        # Get Layout
        lyt = aprx.listLayouts(lyt_template)[0]

        # List elements
        elm = lyt.listElements("TEXT_ELEMENT")

        # Replace elements
        for e in elm:
            if e.name in mapsattr:
                if type(r[e.name]) == float:
                    e.text = str(r[e.name]).replace('.', ',')
                else:
                    e.text = str(r[e.name])
        
        lyt.exportToJPEG(os.path.join(
            outmaps, '{}.jpg'.format(r.slug)), resolution=500)
        
        aprx.saveACopy(os.path.join(outmaps, '{}.aprx'.format(r.slug)))
    
    return outmaps


def layoutv1_nmaps(nmaps, mxd, geodata, mapstbl, lyttmp, mapst, lyrints, outmaps):
    """
    Layout v1 with N maps
    """

    import arcpy
    import os
    from glass.ng.rd import tbl_to_obj

    mapstodo = tbl_to_obj(mapstbl)

    return outmaps

