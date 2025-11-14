# Excel files Properties

import pandas as pd

def list_sheets(xlsPath, api='pandas'):
    """
    Return sheets name in one XLS file
    """

    if api != 'pandas':
        import xlrd
    
        xlsFile = xlrd.open_workbook(xlsPath)
    
        sheets = [sheet.name for sheet in xlsFile.sheets()]
    
        return sheets

    else:
        tbl = pd.ExcelFile(xlsPath)

        return tbl.sheet_names


def cols_by_sheets(xlsx):
    """
    Return dict with sheet names as keys and
    columns values as values
    """

    df = pd.read_excel(xlsx, sheet_name=None)
    sheet_names = list_sheets(xlsx)

    sheets_cols = {}
    for sheet in sheet_names:
        if sheet in df.keys():
            col_names = df[sheet].columns.to_list()

            if col_names:
                sheets_cols[sheet] = col_names
    
    return sheets_cols

