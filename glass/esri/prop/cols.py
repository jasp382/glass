"""
Fields Properties
"""

import arcpy

def lst_flds(tbl):
    """
    Return a list with the name of every field in a Feature Class
    """
    
    return [str(f.name) for f in arcpy.ListFields(tbl)]


def get_geom_field(lyr):
    return arcpy.Describe(lyr).shapeFieldName

def type_fields(tbl, field=None):
    """
    Return a dict with the field name as value and the field type as
    value.
    
    If a field is given (string or list), return only the types for
    the columns in the field object.
    
    The field types could be:
    * All - All field types are returned. This is the default.
    * BLOB - Only field types of BLOB are returned.
    * Date - Only field types of Date are returned.
    * Double - Only field types of Double are returned.
    * Geometry - Only field types of Geometry are returned.
    * GlobalID - Only field types of GlobalID are returned.
    * GUID - Only field types of GUID are returned.
    * Integer - Only field types of Integer are returned.
    * OID - Only field types of OID are returned.
    * Raster - Only field types of Raster are returned.
    * Single - Only field types of Single are returned.
    * SmallInteger - Only field types of SmallInteger are returned.
    * String - Only field types of String are returned.
    """
    
    fields_type = {
        str(f.name) : str(f.type) for f in arcpy.ListFields(tbl)
    }
    
    if not field:
        return fields_type
    
    else:
        if type(field) == list:
            for fld in fields_type:
                if fld not in field:
                    del fields_type[fld]
            return fields_type
        
        elif type(field) == str or type(field) == unicode:
            return fields_type[field]