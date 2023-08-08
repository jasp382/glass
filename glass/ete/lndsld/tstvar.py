"""
Tools for testing variables

TODO: Think more deeply about the organization of this file
"""


def conditional_dependence(movs, indp):
    """
    Estimate conditional dependence between several rasters
    """
    
    import math; from decimal import Decimal
    from glass.prop.feat   import feat_count
    from glass.prop.rst    import get_cellsize, count_cells
    from glass.prop.rst    import frequencies
    
    def foundPredT(dic):
        PredT = 0.0
        for value in dic.keys():
            count = dic[value]
            PredT += (float(value) * count)
        return PredT
    
    def foundTStd(dic, c):
        TVar = 0.0
        for value in dic.keys():
            count = dic[value]
            TVar += (float(value) * count * c)**2
        TStd = math.sqrt(TVar)
        return TStd
    
    def calcCondIndp(Z):
        pi = math.pi
        const6 = 0.2316419
        b1 = 0.31938153
        b2 = -0.356563782
        b3 = 1.781477937
        b4 = -1.821255978
        b5 = 1.330274429 
        Z = float(Z)
        X = Z
        if X < 0.0: X = -Z
        t = 1.0 / (const6 * X + 1.0)
        pid = 2.0 * pi
        XX = -X * X / 2.0
        XX = math.exp(XX) / math.sqrt(pid)
        PZ = (b1 * t) + (b2 * t *t) + (b3 * (t**3)) + (b4 * (t**4)) + (b5 * (t**5))
        PZ = 1.0 - (PZ * XX)
        if Z < 0: PZ = 1.0 - PZ
        return PZ
    
    # Count phenomena ocorrences - total number of landslides
    ExpNumTP = Decimal(feat_count(movs, gisApi='ogr'))
    # Count the number of cell raster
    NrCell = count_cells(indp[0])
    # Get Cellsize of the raster's
    cellsize = Decimal(get_cellsize(indp[0], gisApi='gdal'))
    # Calculate UnitArea
    area_km = Decimal(((cellsize * cellsize) * NrCell) / 1000000.0)
    UnitArea = Decimal((area_km / ExpNumTP) / 40.0)
    ConvFac =  Decimal((cellsize**2) / 1000000.0 / UnitArea)
    # Count the number of times that one class has representation in the raster; put this associations in a ditionary
    sudoDic = {var: frequencies(var) for var in indp}
    # Calculate Conditional Dependence
    nr = 1
    for rst in indp:
        l_overall = {}; l_ric = {}; l_tac = {}
        # Calculate PredT
        PredT = foundPredT(sudoDic[rst])
        PredT *= ConvFac
        for _rst_ in indp:
            # Calculate TStd
            TStd = foundTStd(sudoDic[_rst_], ConvFac)
            TS = (PredT - ExpNumTP) / TStd
            n = ExpNumTP; T = PredT; P = calcCondIndp(TS) * 100.0
            if P > 50.0: overallCI = 100.0 * (100.0 - P) / 50.0
            else: overallCI = 100.0 * (100.0 - (50.0 + (50.0 - P))) / 50.0
            l_overall[(rst, _rst_)] = "%.2f" % overallCI
            ric = n/T; l_ric[(rst, _rst_)] = "%.2f" % ric
            l_tac[(rst, _rst_)] = "%.2f" % P
        nr+=1
    
    return {
        'OVERALL' : l_overall,
        'RIC' : l_ric,
        'TAC' : l_tac
    }

def MakeRasterPearsonCorrelationMatrix(indV, out):
    """
    Generate Pearson Correlation Matrix based on the distribution of several rasters
    """
    
    import xlwt; import os
    from glass.stats.correlation import pearson_correlation
    
    # Open Report File
    report = xlwt.Workbook()
    book = report.add_sheet('CorrelMatrix')
    
    # Write columns titles
    for i in range(len(indV)):
        book.write(0, i+1, os.path.basename(indV(i)))
        book.write(i+1, 0, os.path.basename(indV(i)))
    
    # Write the Correlation Matrix into the report file
    for i in range(len(indV)):
        for e in range(len(indV)):
            c = raster_pearson_correlation(indV[i], indV[e])
            book.write(i+1, e+1, c)
    report.save(out)


def conditional_dependence_matrix(movs, indp, out):
    """
    Generate Conditional Dependence Matrix
    """
    
    import xlwt
    
    # Open Report File
    xls = xlwt.Workbook()
    bk_overall = xls.add_sheet('Overall')
    bk_ric = xls.add_sheet('RIC')
    bk_tac = xls.add_sheet('TAC')
    
    # Write columns titles
    for i in range(len(indp)):
        bk_overall.write(0, i+1, os.path.basename(indp[i])[:-4])
        bk_overall.write(i+1, 0, os.path.basename(indp[i])[:-4])
        bk_ric.write(0, i+1, os.path.basename(indp[i])[:-4])
        bk_ric.write(i+1, 0, os.path.basename(indp[i])[:-4])
        bk_tac.write(0, i+1, os.path.basename(indp[i])[:-4])
        bk_tac.write(i+1, 0, os.path.basename(indp[i])[:-4])
    
    # Calculate Conditional Dependence
    dicConditionalDependence = conditional_dependence(movs, indp)
    dOverall = dicConditionalDependence['OVERALL']
    dRic = dicConditionalDependence['RIC']
    dTac = dicConditionalDependence['TAC']
    for l in range(len(indp)):
        for c in range(len(indp)):
            bk_overall.write(l+1, i+1, dOverall[(indp[l], indp[c])])
            bk_ric.write(l+1, i+1, dRic[(indp[l], indp[c])])
            bk_tac.write(l+1, i+1, dTac[(indp[l], indp[c])])
    xls.save(out)

