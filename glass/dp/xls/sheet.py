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


def list_sheets(xlsPath):
    """
    Return sheets name in one XLS file
    """
    
    xlsFile = xlrd.open_workbook(xlsPath)
    
    sheets = [sheet.name for sheet in xlsFile.sheets()]
    
    return sheets


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
    
    sheetsN = list_sheets(xlsPath)
    
    return sheetsN[idx]


def copy_sheet_to_file(srcFile, destFile, sheets, newNames=None):
    """
    Copy sheets from one file to another
    """
    
    import os
    import xlrd
    from win32com.client import Dispatch
    
    # Get sheets position
    xlsFile    = xlrd.open_workbook(srcFile)
    sheets_pos = get_sheet_position(xlsFile, sheets)
    del xlsFile
    
    # Check if destFile exists
    # Create it if not exists
    if not os.path.exists(destFile):
        from glass.dp.xls import create_empty_file
        destFile = create_empty_file(destFile, engine="openpyxl")
    
    excelApp = Dispatch("Excel.Application")
    excelApp.Visible = 0
    excelApp.DisplayAlerts = False
    
    wbInXls  = excelApp.Workbooks.Open(Filename=srcFile)
    wbOutXls = excelApp.Workbooks.Open(Filename=destFile)
    
    n_sheet = 1
    for sheet in sheets_pos:
        worksheet = wbInXls.Worksheets(sheets_pos[sheet] + 1)
        
        worksheet.Copy(Before=wbOutXls.Worksheets(n_sheet))
        
        if newNames:
            wbOutXls.Sheets[n_sheet-1].Name = newNames[sheet]
        
        n_sheet += 1
    
    wbInXls.Close(SaveChanges=False)
    wbOutXls.Close(SaveChanges=True)
    
    excelApp.Quit()


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

