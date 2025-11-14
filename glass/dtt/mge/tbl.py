"""
Manage Excel data
"""

def merge_xlsx(tbl_folder, out_table, sheetname=None):
    """
    Get all excel tables in a folder and make one table of them
    """
    
    import pandas
    from glass.pys.oss import lst_ff
    from glass.rd      import tbl_to_obj
    from glass.wt      import obj_to_tbl

    if type(tbl_folder) != list:
        tables = lst_ff(tbl_folder, file_format=['.xls', '.xlsx'])
    
    else:
        tables = tbl_folder
    
    dfs = [tbl_to_obj(table) for table in tables]
    
    result = pandas.concat(dfs)
    
    out_table = obj_to_tbl(result, out_table, sheetsName=sheetname)
    
    return out_table


def copy_sheet_to_file(srcFile, destFile, sheets, newNames=None):
    """
    Copy sheets from one file to another
    """
    
    import os
    import xlrd
    from win32com.client import Dispatch
    from glass.tbl.xls.sheet import get_sheet_position
    
    # Get sheets position
    xlsFile    = xlrd.open_workbook(srcFile)
    sheets_pos = get_sheet_position(xlsFile, sheets)
    del xlsFile
    
    # Check if destFile exists
    # Create it if not exists
    if not os.path.exists(destFile):
        from glass.tbl.xls import create_empty_file
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


def sheets_into_file(xlsFolder, outXls, intSheets):
    """
    For each xls file in one folder, pick one interest sheet
    and save all sheets in a single file
    """
    
    from glass.pys.oss       import lst_ff, fprop
    
    xls_s = lst_ff(xlsFolder, file_format=['.xls', '.xlsx'])
    
    for xlsPath in xls_s:
        copy_sheet_to_file(
            xlsPath, outXls, intSheets,
            {intSheets : fprop(xlsPath, 'fn', forceLower=True)}
        )
    
    return outXls