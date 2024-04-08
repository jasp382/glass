"""
Working with sheets
"""

import xlrd

def get_sheet_obj(xls_obj, name=None, index=None):
    if name and not index:
        return xls_obj.sheet_by_name(name)
    
    elif not name and index:
        return xls_obj.sheet_by_index(index)
    
    elif name and index:
        return xls_obj.sheet_by_index(index)
    
    elif not name and not index:
        return xls_obj.sheet_by_index(0)


def get_sheet_position(xlsObj, sheetNames):
    """
    Return sheet position by name
    """
    
    from glass.pys  import obj_to_lst
    
    names = obj_to_lst(sheetNames)
    
    d = {}
    c = 0
    for sh in xlsObj.sheets():
        if sh.name in names:
            d[sh.name] = c
        
        c += 1
    
    return d

def get_sheetname_by_idx(xlsPath, idx):
    """
    Return sheet name using sheet position
    """

    from glass.prop.xls import list_sheets
    
    sheetsN = list_sheets(xlsPath)
    
    return sheetsN[idx]


def rename_sheets_replacing(table, tobeReplaced, replacement):
    """
    Replace str in sheets name for another
    """
    
    from win32com.client import Dispatch
    
    excelApp               = Dispatch("Excel.Application")
    excelApp.Visible       = 0
    excelApp.DisplayAlerts = False
    
    wbInXls = excelApp.Workbooks.Open(Filename=table)
    
    for sheet in wbInXls:
        name = sheet.Name
        name = name.replace(tobeReplaced, replacement)
        
        sheet.Name = name
    
    wbInXls.Close(SaveChanges=True)
    
    excelApp.Quit()

