import arcpy


def legend_replace_objects(
    mxd, new_mxd, old_suffix, new_suffix, exportMap=False):
    """
    Replace elements of a legend by the ones outside the 
    layout view. The replacement is done using the graphic elements
    name.
    Name of elements to be replaced:
    - old_suffix1
    - old_suffix2
    - old_suffixn
    Name of elements that will replace the others
    - new_suffix1
    - new_suffix2
    - new_suffixn
    The element with the name 'new_suffix1' will replace the element
    with the name 'old_suffix1' and so one
    """
    
    import os
    from glass.esri.lyout.tbx.wmap import write_map
    
    # Open mxd
    __mxd = arcpy.mapping.MapDocument(mxd)
    
    graphic_el = arcpy.mapping.ListLayoutElements(__mxd, "GRAPHIC_ELEMENT")
    
    old_elements = []
    new_elements = []
    for e in graphic_el:
        if old_suffix in str(e.name):
            old_elements.append(e)
        elif new_suffix in str(e.name):
            new_elements.append(e)
    
    if len(old_elements) != len(new_elements):
        raise ValueError('The number of old and new elements is not the same')
    
    for i in new_elements:
        el_number = i.name.strip(new_suffix)
        for e in old_elements:
            __el_number = e.name.strip(old_suffix)
            if el_number == __el_number:
                i.elementPositionX = e.elementPositionX
                i.elementPositionY = e.elementPositionY
                i.elementWidth = e.elementWidth
                i.elementHeight = e.elementHeight
    
    for el in old_elements:
        el.delete()
            
    if exportMap:
        outmap = write_map(
            __mxd, os.path.splitext(new_mxd)[0] + '.jpg')
    
    __mxd.saveACopy(new_mxd)


def folder_legend_replace_objects(folder_mxd, old_sufix, new_sufix, output_mxd):
    """
    Execute the method legend replace objects for every mxd in a folder
    """
    
    import os
    from glass.pys.oss import lst_ff
    
    mxds = lst_ff(folder_mxd, file_format='.mxd')
    
    for mxd in mxds:
        legend_replace_objects(
            mxd,
            os.path.join(output_mxd, os.path.basename(mxd)),
            old_suffix=old_sufix, new_suffix=new_sufix,
            exportMap=True
        )

