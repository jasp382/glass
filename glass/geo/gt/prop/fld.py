"""
Fields Properties
"""

from osgeo           import ogr
from glass.geo.gt.prop.ff import drv_name

def map_fldCode_fldName(code=None, name=None):
    """
    Return the Field Type Name or the Field Type Code for a given
    code or name
    """
    
    mapObj = {
        2  : 'Real',
        4  : 'String',
        12 : 'Integer64'
    }
    
    if code and not name:
        if code in mapObj:
            return mapObj[code]
        else:
            raise ValueError('Code not referenced')
    
    elif not code and name:
        if name in mapObj.values():
            for __code in mapObj:
                if str(name) == mapObj[__code]:
                    return __code
        
        else:
            raise ValueError('Name not referenced')
    
    elif not code and not name:
        return mapObj


def map_pyType_fldCode(pyObj):
    """
    Return the code of the field type necessary to store that type of 
    python objects
    """
    
    if type(pyObj) == float:
        return 2
    elif type(pyObj) == int:
        return 12
    elif type(pyObj) == str:
        return 4
    else:
        raise ValueError((
            "Type of the given pyObj hasn't correspondence to a field code"
        ))


def pandas_map_ogrType(type_):
    __types = {
        'int32'   : ogr.OFTInteger,
        'int64'   : ogr.OFTInteger,
        'float32' : ogr.OFTReal,
        'float64' : ogr.OFTReal,
        'object'  : ogr.OFTString
    }
    
    return __types[type_]

def ogrFieldsDefn_from_pandasdf(df):
    """
    Return OGR Field Defn for every column in Pandas DataFrame
    """
    
    typeCols = dict(df.dtypes)
    
    return {col : pandas_map_ogrType(
        str(typeCols[col])) for col in typeCols}

def ogr_list_fields_defn(shp):
    """
    Return a dict with the field name as key and the field definition as value
    
    Field defn is the same of saying name + type
    """
    
    if type(shp) == ogr.Layer:
        lyr = shp
        c   = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp, 0) 
        lyr = data.GetLayer()
        c   = 1
    
    defn = lyr.GetLayerDefn()
    
    fields = {}
    for i in range(0, defn.GetFieldCount()):
        fdefn = defn.GetFieldDefn(i)
        fieldType = fdefn.GetFieldTypeName(fdefn.GetType())
        
        fields[fdefn.name] = {fdefn.GetType(): fieldType}
    
    if c:
        del lyr
        data.Destroy()
    
    return fields


def lst_cols(shp):
    """
    Return columns in GeoFile
    """

    from glass.geo.gt.fmshp import shp_to_obj

    df = shp_to_obj(shp)

    cols = df.columns.values

    del df

    return cols

