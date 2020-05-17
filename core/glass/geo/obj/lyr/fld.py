"""
Fields in OGR Layers
"""

from osgeo import ogr

def fields_to_lyr(lyr, fields):
    """
    Add fields to Layer Object

    TODO: Check if fields is a dict
    """

    if type(lyr) != ogr.Layer:
        raise ValueError('lyr must be a OGR Layer')

    for fld in fields:
        lyr.CreateField(ogr.FieldDefn(fld, fields[fld]))
    
    return lyr


def copy_flds(inLyr, outLyr, __filter=None):
    
    if __filter:
        __filter = [__filter] if type(__filter) != list else __filter
    
    inDefn = inLyr.GetLayerDefn()
    
    for i in range(0, inDefn.GetFieldCount()):
        fDefn = inDefn.GetFieldDefn(i)
        
        if __filter:
            if fDefn.name in __filter:
                outLyr.CreateField(fDefn)
            
            else:
                continue
        
        else:
            outLyr.CreateField(fDefn)
    
    del inDefn, fDefn

