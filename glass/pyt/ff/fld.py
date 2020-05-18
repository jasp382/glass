"""
Fields in Files
"""

def cols_xlsx(ff, sheet=None):
    """
    Get names of columns in XLSX File
    """
    
    import pandas
    
    sheet = 0 if not sheet else sheet
    
    df = pandas.read_excel(
        ff, sheet, encoding='utf-8',
        dtype='object',
        nrows=1
    )
    
    return df.columns.values


def cols_name(ff, sheetName=None, sheetIdx=None):
    """
    Get Columns Name in File, regardeless the type of file
    """
    
    from glass.pyt.oss import fprop
    
    fFormat = fprop(ff, 'ff')
    
    if fFormat == '.xlsx' or fFormat == '.xls':
        from glass.pyt.xls.fld import col_name
        
        cols = col_name(ff, sheet_name=sheetName, sheet_index=sheetIdx)
    
    else:
        raise ValueError(
            'File format is not valid!'
        )
    
    return cols

