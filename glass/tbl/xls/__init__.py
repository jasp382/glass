"""
Methods for processing xls files
"""


def create_empty_file(path, engine='xlwt'):
    """
    Create Empty xls file
    """
    
    if engine == 'xlwt':
        import xlwt
    
        xls = xlwt.Workbook()
    
        sheet = xls.add_sheet("Folha1")
    
        xls.save(path)
    
    elif engine == 'openpyxl':
        import openpyxl
        
        xls = openpyxl.Workbook()
        
        xls.save(path)
    
    return path