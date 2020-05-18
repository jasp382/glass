"""
Splitting with OGR
"""


def splitShp_by_range(shp, nrFeat, outFolder):
    """
    Split one feature class by range
    """
    
    import os
    from glass.pyt.oss      import fprop
    from glass.geo.gt.prop.feat import feat_count, lst_fld
    from glass.geo.gt.attr      import sel_by_attr
    
    rowsN = feat_count(shp, gisApi='ogr')
    
    nrShp = int(rowsN / float(nrFeat)) + 1 if nrFeat != rowsN else 1
    
    fields = lst_fld(shp)
    
    offset = 0
    exportedShp = []
    for i in range(nrShp):
        f = fprop(shp, ['fn', 'ff'], forceLower=True)
        outShp = sel_by_attr(
            shp,
            "SELECT {cols}, geometry FROM {t} ORDER BY {cols} LIMIT {l} OFFSET {o}".format(
                t=os.path.splitext(os.path.basename(shp))[0],
                l=str(nrFeat), o=str(offset),
                cols=", ".join(fields)
            ),
            os.path.join(outFolder, "{}_{}{}".format(
                f['filename'], str(i), f['fileformat']
            )), api_gis='ogr'
        )
        
        exportedShp.append(outShp)
        offset += nrFeat
    
    return exportedShp


"""
Split Excel tables
"""

def split_table_by_number(xlsTable, row_number, output,
                          sheetName=None, sheetIndex=None):
    """
    Split a table by row number
    
    Given a number of rows, this method will split an input table
    in several tables with a number of rows equal to row_number.
    
    TODO: Do it with Pandas
    """
    
    import xlrd;          import xlwt
    from glass.fm          import tbl_to_obj
    from glass.pyt.xls.fld import col_name
    
    COLUMNS_ORDER = col_name(
        xlsTable, sheet_name=sheetName, sheet_index=sheetIndex
    )
    
    DATA = tbl_to_obj(xlsTable,
        sheet=sheetIndex if sheetIndex else sheetName, output='array'
    )
    
    # Create output
    out_xls = xlwt.Workbook()
    
    l = 1
    s = 1
    base = sheetName if sheetName else 'data'
    for row in DATA:
        if l == 1:
            sheet = out_xls.add_sheet('{}_{}'.format(base, s))
            
            # Write Columns
            for col in range(len(COLUMNS_ORDER)):
                sheet.write(0, col, COLUMNS_ORDER[col])
        
        for col in range(len(COLUMNS_ORDER)):
            sheet.write(l, col, row[COLUMNS_ORDER[col]])
        
        l += 1
        
        if l == row_number + 1:
            l = 1
            s += 1
    
    # Save result
    out_xls.save(output)

