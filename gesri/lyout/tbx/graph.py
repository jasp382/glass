"""
Deal with graphic elements
"""

import arcpy

def get_elem_by_name(mxd, names, elm_type="TEXT_ELEMENT"):
    elms = arcpy.mapping.ListLayoutElements(
        mxd, elm_type)
    
    names = [names] if type(names) == str or type(names) == unicode else \
        names if type(names) == list or type(names) == dict else None
    
    if not names:
        raise ValueError('names should be a string, unicode, list or dict')
    
    interest_elem = {}
    for elm in elms:
        if str(elm.name) in names:
            interest_elem[elm.name] = elm
    
    return interest_elem


def get_elem_by_prefix(mxd_obj, prefix,
                       elm_type="TEXT_ELEMENT"):
    elms = arcpy.mapping.ListLayoutElements(
        mxd_obj, elm_type
    )
    
    elements = []
    for e in elms:
        if prefix in str(e.name):
            elements.append(e)
    
    return elements

