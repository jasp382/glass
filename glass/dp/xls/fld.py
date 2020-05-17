"""
Get Information about the fields in a excel table
"""

def get_columns_position(sheet_object, cols_name):
    """
    Given the name, find the column position in the file
    
    cols_position = {
        column_name: position_index, ...
    }
    """
    
    from glass.pys  import obj_to_lst
    
    cols_name = obj_to_lst(cols_name)
    
    if not cols_name:
        raise ValueError('cols_name should be a string or a list')
    
    
    cols_position = {}
    
    for col in range(sheet_object.ncols):
        name = str(sheet_object.cell(0, col).value)
        if name in cols_name:
            cols_position[name] = col
    
    return cols_position


def get_columns_position_outside_options(sheet_obj, cols_name):
    """
    Return a dict with the name and position of cols not in cols_name
    
    cols_position = {
        column_name: position_index, ...
    }
    """
    
    cols_position = {}
    
    for col in range(sheet_obj.ncols):
        name = str(sheet_obj.cell(0, col).value)
        if name not in cols_name:
            cols_position[name] = col
    
    if u'' in cols_position.keys():
        del cols_position[u'']
    
    if '' in cols_position.keys():
        del cols_position['']
    
    return cols_position


def col_name(xls_file, sheet_name=None, sheet_index=None):
    
    import xlrd
    from glass.dp.xls.sheet import get_sheet_obj
    
    try:
        xls = xlrd.open_workbook(xls_file)
    
        sheet = get_sheet_obj(xls, name=sheet_name, index=sheet_index)
    
    except:
        sheet = xls_file
    
    colname = [sheet.cell(0, x).value for x in range(sheet.ncols)]
    
    try:
        xls.release_resources()
    except:
        pass
    
    return colname

