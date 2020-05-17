"""
Write Charts in XLS Files
"""

def barchart_in_xls_from_df(df, outxls, seriesCols, xAxisCol):
    """
    Pandas Dataframe to barchart in XLS File
    """
    
    import pandas
    from vincent.colors import brews
    
    cols = list(df.columns.values)
    graphCols = [xAxisCol] + seriesCols
    colsPos = {cols[i] : i for i in range(
        len(cols)) if cols[i] in graphCols}
    
    writer = pandas.ExcelWriter(outxls, engine='xlsxwriter')
    
    df.to_excel(writer, sheet_name='sheet1')
    
    workbook  = writer.book
    worksheet = writer.sheets['sheet1']
    chart     = workbook.add_chart({"type" : "column"})
    
    df_rows = df.shape[0]
    c = 1
    colorRamp = "Spectral"
    
    for serie in seriesCols:
        if c not in range(len(brews[colorRamp])):
            c = 1
            colorRamp = "Set3"
        
        chart.add_series({
            "name"       : ["sheet1", 0, colsPos[serie] + 1],
            "categories" : [
                "sheet1", 1, colsPos[xAxisCol] + 1,
                df_rows ,    colsPos[xAxisCol] + 1
            ],
            "values"     : [
                "sheet1", 1, colsPos[serie] + 1,
                df_rows ,    colsPos[serie] + 1
            ],
            "fill"       : {"color" : brews[colorRamp][c - 1]},
            "gap": 300
        })
        c += 1
    
    chart.set_y_axis({'major_gridlines' : {'visible' : false}})
    worksheet.insert_chart('K2', chart)
    writer.save()
    
    del writer
    
    return outxls

