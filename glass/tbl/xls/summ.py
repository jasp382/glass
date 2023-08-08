"""
Summarize things
"""


def list_unique_values_column(sheet_obj, col_position):
    """
    Return a list with all values in a column
    
    for the column:
      | column |
    0 |  2000  |
    1 |  2001  |
    2 |  2000  |
    3 |  2002  |
    4 |  2003  |
    5 |  2004  |
    6 |  2005  |
    7 |  2006  |
    8 |  2004  |
    9 |  2005  |
    10|  2007  |
    11|  2001  |
    12|  2000  |
    
    Return a list as:
    [2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007]
    
    The value appear only once in the returned object...
    """
    
    l = []
    for line in range(1, sheet_obj.nrows):
        value = sheet_obj.cell(line, col_position).value
        if value not in l:
            l.append(value)
    
    while u'' in l:
        l.remove(u'')
    
    while '' in l:
        l.remove('')
    
    return l


def count_values_column(sheet_obj, col_pos, ref_values=None):
    """
    Count the occourences of a value in a column
    
    ref_values = [value1, value2, ..., valuen]
    
    output = {
        value1: count,
        value2: count,
        ...,
        valuen: count
    }
    """
    
    result = {}
    
    for row in range(1, sheet_obj.nrows):
        val = sheet_obj.cell(row, col_pos).value
        
        if ref_values:
            if val in ref_values:
                if val not in result.keys():
                    result[val] = 1
                else:
                    result[val] += 1
        
        else:
            if val not in result.keys():
                result[val] = 1
            else:
                result[val] += 1
    
    return result


def count_values_column_if_entity_exists(sheet_obj, col_pos, entities, ref_values=None,
                                         entitie_col=0):
    result = {}
    
    for row in range(1, sheet_obj.nrows):
        val = sheet_obj.cell(row, col_pos).value
        entity = sheet_obj.cell(row, entitie_col).value
        
        if ref_values:
            if val in ref_values and entity in entities:
                if val not in result.keys():
                    result[val] = 1
                else:
                    result[val] += 1
        else:
            if entity in entities:
                if val not in result.keys():
                    result[val] = 1
                else:
                    result[val] += 1
    
    return result


def count_values_column_by_entity_property(sheet_obj, col_pos, __property, entities,
                                           ref_values, entitie_col=0):
    """
    Count the occourences of a value filtered by a property of an entity
    
    entities = {'entitie': 'property'}
    
    If the entity does not exists in the entities dict, the value will not be in
    the result output
    """
    
    result = {}
    
    for row in range(1, sheet_obj.nrows):
        val = sheet_obj.cell(row, col_pos).value
        entity = sheet_obj.cell(row, entitie_col).value
        
        if entity in entities.keys():
            if __property == entities[entity]:
                if val in ref_values:
                    if val not in result.keys():
                        result[val] = 1
                    else:
                        result[val] += 1
    
    return result

