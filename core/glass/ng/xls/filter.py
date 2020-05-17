"""
Filter data and export to a new table
"""

def export_cells_not_in(inTable, noTable, outTable, inSheet, noSheet, inFID,
                        noFID):
    """
    Export to a new file the cells of in Table not in noTable
    """
    
    import xlrd;           import xlwt
    from glass.ng.rd       import tbl_to_obj
    from glass.ng.xls.fld  import col_name, get_columns_position
    from glass.ng.xls.summ import list_unique_values_column
    
    # TODO: check if tables are xls
    
    # Get Data
    inData  = tbl_to_obj(inTable, sheet=inSheet, output='array')
    COLUMNS = col_name(inTable, sheet_name=inSheet)
    
    # From noDATA, get IDS that will not be in the outTable
    noXls = xlrd.open_workbook(noTable)
    _noSheet = noXls.sheet_by_name(noSheet)
    colsPosition = get_columns_position(_noSheet, noFID)
    noFIDS = list_unique_values_column(_noSheet, colsPosition[noFID])
    
    # Create Output
    out_xls = xlwt.Workbook()
    new_sheet = out_xls.add_sheet(inSheet)
    
    # Write columns titles
    for c in range(len(COLUMNS)):
        new_sheet.write(0, c, COLUMNS[c])
    
    # Write data not in noData
    l = 1
    for row in inData:
        if row[inFID] not in noFIDS:
            c = 0
            for col in COLUMNS:
                new_sheet.write(l, c, row[col])
                c += 1
            
            l += 1
    
    out_xls.save(outTable)
    
    return outTable

