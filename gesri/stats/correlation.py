"""
Tools applying statistic methods using ArcGIS and ArcPy
"""


def raster_pearson_correlation(x, y):
    """
    Pearson correlation between two raster images
    
    The images have to have the same reading order
    """
    
    import numpy
    from glass.fm.rst import toarray_varcmap as rst_to_array
    
    vx = rst_to_array(x, flatten=True, with_nodata=False)
    vy = rst_to_array(y, flatten=True, with_nodata=False)
    
    cof = numpy.corrcoef(vx, vy)[0, 1]
    
    return cof


def pearson_correlation_matrix_from_dbase(dbf, fields, outFile):
    """
    Estimate the correlation between some fields of a dbase table, specified
    by the variable fields
    """
    
    import arcpy
    import numpy
    import os
    import xlwt
    
    if type(fields) != list:
        raise ValueError("fields must be a list")
    
    cursor = arcpy.SearchCursor(dbf)
    
    linha = cursor.next()
    
    corrMatrix = {}
    while linha:
        for field in fields:
            v = linha.getValue(field)
            
            if field not in corrMatrix:
                corrMatrix[field] = [v]
            
            else:
                corrMatrix[field].append(v)
        
        linha = cursor.next()
    
    xls = xlwt.Workbook()
    sht = xls.add_sheet(os.path.splitext(os.path.basename(dbf))[0])
    
    # Write columns and rows titles
    for i in range(len(fields)):
        # COLUMNS
        sht.write(0, i+1, fields[i])
        # ROWS
        sht.write(i+1, 0, fields[i])
    
    # Write coeficients
    for i in range(len(fields)):
        for e in range(len(fields)):
            sht.write(i+1, e+1, numpy.corrcoef(
                numpy.array(corrMatrix[fields[i]]),
                numpy.array(corrMatrix[fields[e]])
            )[0, 1])
    
    # Save result
    xls.save(outFile)

