# -*- coding: utf-8 -*-
"""
MODULE: arcgis surface
PURPOSE: Tools for modelling surface with arcgis
"""


import arcpy

def slope(demRst, slopeRst, data=None):
    """
    Run Slope
    """
    
    data = "PERCENT_RISE" if not data else data
    
    arcpy.gp.Slope_sa(demRst, slopeRst, data)
    
    return slopeRst


def hillshade(dem, out):
    """
    Generate hillshade raster
    """
    
    arcpy.gp.Hillshade_sa(dem, out, "315", "45", "NO_SHADOWS", "2")
    return out


def aspect(dem, aspect, reclass=None):
    """
    Return Aspect raster reclassified or not
    """
    
    import os
    
    outAspect = aspect if not reclass else \
        os.path.join(
            os.path.dirname(aspect),
            '{n}_original{f}'.format(
                n=os.path.splitext(os.path.basename(aspect))[0],
                f=os.path.splitext(os.path.basename(aspect))[1]
            )
        )
    
    arcpy.gp.Aspect_sa(dem, outAspect)
    
    if reclass:
        from glass.cpu.arcg.lyr          import raster_lyr
        from glass.cpu.arcg.spanlst.rcls import reclassify
        from glass.cpu.arcg.mng.fld      import add_field
        
        __rules = (
            "-1 0 1;"
            "0 22,5 2;"
            "22,5 67,5 3;"
            "67,5 112,5 4;"
            "112,5 157,5 5;"
            "157,5 202,5 6;"
            "202,5 247,5 7;"
            "247,5 292,5 8;"
            "292,5 337,5 9;"
            "337,5 360 2"
        )
        
        reclassify(outAspect, "Value", __rules, aspect, template=outAspect)
        
        d = {
            1: 'Flat', 2: 'North', 3: 'Northeast', 4: 'East',
            5: 'Southeast', 6: 'South', 7: 'Southwest', 8: 'West',
            9: 'Northwest'
        }
        
        add_field(aspect, 'aspect', "TEXT", "15")
        
        cursor = arcpy.UpdateCursor(rst_lyr(aspect))
        for lnh in cursor:
            __val = int(lnh.getValue("Value"))
            
            lnh.setValue('aspect', d[__val])
            
            cursor.updateRow(lnh)
        
        del cursor, lnh


def viewshed(inRaster, observerFeat, output,
             extRaster=None, snapRaster=None, maskRaster=None):
    """
    Viewshed used by arcpy
    """
    
    if extRaster:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = extRaster
    
    if snapRaster:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snapRaster
    
    if maskRaster:
        tempMask = arcpy.env.mask
        arcpy.env.mask = maskRaster
    
    arcpy.gp.Viewshed_sa(
        inRaster, observerFeat, output,
        "1", "FLAT_EARTH", "0,13", ""
    )
    
    if extRaster:
        arcpy.env.extent = tempEnvironment0
    
    if snapRaster:
        arcpy.env.snapRaster = tempSnap
    
    if maskRaster:
        arcpy.env.mask = tempMask
    
    return output


def vertente_profile(dem, outrst, reclass=None):
    """
    Cria Perfil Vertente
    """
    
    
    arcpy.gp.Curvature_sa(mdt, "curvatura.tif", "1", "", "")
    saida = workspace + "\\" + str(saida) + ".tif"
    tempEnvironment0 = arcpy.env.extent
    arcpy.env.extent = mdt
    arcpy.gp.Reclassify_sa(workspace + "\\curvatura.tif", "Value", "-72 -0,025000000000000001 1;-0,025000000000000001 -0,0025000000000000001 2;-0,0025000000000000001 0,0025000000000000001 3;0,0025000000000000001 0,025000000000000001 4;0,025000000000000001 70 5", saida, "DATA")
    arcpy.env.extent = tempEnvironment0
    layer = arcpy.MakeRasterLayer_management(saida, "lyr", "", "", "1")
    arcpy.AddField_management(layer, "classe", "TEXT", "50", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    dic = {1: "DoMenoraneg0.025", 2: "neg0.25aneg0.0025",3:"neg0.0025apos0.0025", 4:"0.0025a0.025", 5:"0.025aMaior"}
    cs = arcpy.UpdateCursor(layer)
    for linha in cs:
        value = int(linha.getValue("Value"))
        for chave in dic.keys():
            if value == chave:
                linha.setValue("classe", dc_exposicoes[chave])
                cs.updateRow(linha)
    shutil.rmtree(workspace)


def inverso_topografico(dem, outrst):
    """
    Inverso do �ndice Topogr�fico
    """
    
    import arcpy, os, shutil
    workspace = "C:\\temporario"
    os.mkdir(workspace)
    arcpy.env.workspace = workspace
    arcpy.gp.Slope_sa(mdt, "slope.tif", "DEGREE")
    arcpy.gp.Fill_sa(mdt, "fill.tif", "")
    arcpy.gp.FlowDirection_sa(workspace + "\\fill.tif", "direcao.tif", "NORMAL", "")
    arcpy.gp.FlowAccumulation_sa(workspace + "\\direcao.tif", "rst_acumulacao.tif", "", "FLOAT")
    declv = arcpy.MakeRasterLayer_management(workspace + "\\slope.tif", "declv", "", "", "1")
    acumu = arcpy.MakeRasterLayer_management(workspace + "\\rst_acumulacao.tif", "acum", "", "", "1")
    expressao = "(" + "\"declv\"" + " / " + "\"acum\")"
    tempEnvironment0 = arcpy.env.extent
    arcpy.env.extent = mdt
    arcpy.gp.RasterCalculator_sa(expressao, "calculadora.tif")
    arcpy.env.extent = tempEnvironment0
    tempEnvironment0 = arcpy.env.extent
    arcpy.env.extent = mdt    
    arcpy.gp.Reclassify_sa(workspace + "\\calculadora.tif", "Value", "0 1;0 0,001 2;0,001 0,01 3;0,01 0,10000000000000001 4;0,10000000000000001 70 5;NODATA 5", "reclss.tif", "DATA")
    arcpy.env.extent = tempEnvironment0
    tempEnvironment0 = arcpy.env.extent
    arcpy.env.extent = mdt    
    arcpy.gp.Reclassify_sa(workspace + "\\slope.tif", "Value", "0 70 0", "mascara.tif", "DATA")
    arcpy.env.extent = tempEnvironment0
    mascara = arcpy.MakeRasterLayer_managemnet(workspace ++ "\\mascara.tif", "mascara", "", "", "1")
    inverso_topo = arcpy.MakeRasterLayer_managemnet(workspace ++ "\\reclss.tif", "inverso_temp", "", "", "1")
    tempEnvironment0 = arcpy.env.extent
    arcpy.env.extent = mdt
    arcpy.gp.RasterCalculator_sa("\"mascara\" + \"inverso_temp\"", saida + ".tif")
    arcpy.env.extent = tempEnvironment0
    lyr = arcpy.MakeRasterLayer_management(workspace + "\\" + saida + ".tif", "final", "", "", "1")
    arcpy.AddField_management(layer, "classe", "TEXT", "50", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    dic = {1: "0", 2: "0a0,001",3:"0,001a0,01", 4:"0,01a0,1", 5:"maior0,1"}
    cs = arcpy.UpdateCursor(layer)
    for linha in cs:
        value = int(linha.getValue("Value"))
        for chave in dic.keys():
            if value == chave:
                linha.setValue("classe", dc_exposicoes[chave])
                cs.updateRow(linha)
    shutil.rmtree(workspace)

