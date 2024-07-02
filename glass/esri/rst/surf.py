"""
MODULE: arcgis surface
PURPOSE: Tools for modelling surface with arcgis
"""


import arcpy


def dem_from_tin(
    countors, col, bbox_dem,
    cellsize, outdem, bbox_tin=None, hidrology=None,
    snapRst=None, prj=None, out_tin=None):
    """
    Create a Digital Elevation Model based on a TIN
    """
    
    import os
    from glass.pys.oss      import fprop, mkdir
    from glass.pys.tm       import now_as_str
    from glass.esri.rd.shp  import shp_to_lyr
    from glass.esri.ddd.tin import countours_to_tin
    from glass.esri.it      import tin_to_raster
    from glass.esri.rst.ovl import clip_rst
    
    ws = mkdir(os.path.join(
        os.path.dirname(outdem),
        now_as_str(utc=True)
    ), overwrite=True)

    oprop = fprop(outdem, ['fn', 'ff'])
    oname, of = oprop['filename'], oprop['fileformat']
    cname = fprop(countors, 'fn')
    tmpdem = outdem if not bbox_tin else os.path.join(ws, f'tmp_{oname}{of}')

    otin = out_tin if out_tin else os.path.join(ws, f'tin_{oname}')
    
    # Check Extension
    #arcpy.CheckOutExtension("3D")
    srs = arcpy.SpatialReference(f'{os.path.splitext(countors)[0]}.prj') \
        if not prj else arcpy.SpatialReference(prj) if type(prj) == int \
        else None
    
    if not srs:
        raise ValueError('Unknown Spatial Reference System')
    
    # Create TIN
    tin = countours_to_tin(
        countors, col,
        bbox_tin if bbox_tin else bbox_dem,
        prj, otin, hidrology
    )

    # TIN2Raster
    rst_tin = tin_to_raster(
        tin, cellsize, tmpdem,
        snap_rst=snapRst
    )

    if bbox_tin:
        # Clip Raster
        lmt_clip = shp_to_lyr(bbox_dem)
        dem_clip = clip_rst(rst_tin, lmt_clip, outdem, snap=snapRst)
    
    return outdem


def loop_dem_from_tin(countors_fld, elevField, bound_tin_fld, bound_mdt_fld,
                 cellsize, w, fld_outputs, snapRst=None, prj=None,
                 shpFormat='.shp', rstFormat='.tif'):
    """
    Create a Digital Elevation Model based on a TIN in loop
    
    NOTES:
    * Related countours and boundaries should have the same name in the
    respective folder
    
    * elevField should be the same in all countors_fld
    """
    
    import os
    from glass.pys.oss import lst_ff
    
    # List files
    countours = lst_ff(countors_fld, file_format=shpFormat)
    
    rstFormat = rstFormat if rstFormat[0] == '.' else '.' + rstFormat
    shpFormat = shpFormat if shpFormat[0] == '.' else '.' + shpFormat
    
    for shp in countours:
        shpFilename = os.path.basename(shp)
        
        dem_from_tin(
            shp, elevField,
            os.path.join(bound_tin_fld, shpFilename),
            os.path.join(bound_mdt_fld, shpFilename),
            cellsize,
            w,
            os.path.join(
                fld_outputs,
                os.path.splitext(shpFilename)[0] + rstFormat
            ),
            snapRst=snapRst,
            prj=prj
        )


def slope(dem, sloperst, data=None):
    """
    Run Slope

    data OPTIONS:
    * DEGREE
    * PERCENT RISE
    """

    from arcpy.sa import Slope
    
    data = "DEGREE" if not data else data

    arcpy.env.extent = dem
    arcpy.env.snapRaster = dem
    
    slp = Slope(dem, data)

    slp.save(sloperst)
    
    return sloperst, slp


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

    from arcpy.sa import Aspect
    
    asp = Aspect(dem)
    
    if reclass:
        from glass.esri.rst.rcls import rcls_rst
        from glass.esri.tbl.col  import add_col

        _rules = [
            [-1, 0, 1],
            [0, 22.5, 2],
            [22.5, 67.5, 3],
            [67.5, 112.5, 4],
            [112.5, 157.5, 5],
            [157.5, 202.5, 6],
            [202.5, 247.5, 7],
            [247.5, 292.5, 8],
            [292.5, 337.5, 9],
            [337.5, 360, 2],
        ]
        
        aspect, asp = rcls_rst(asp, "Value", _rules, aspect, dem, isrange=True)
        
        d = {
            1: 'Flat', 2: 'North', 3: 'Northeast', 4: 'East',
            5: 'Southeast', 6: 'South', 7: 'Southwest', 8: 'West',
            9: 'Northwest'
        }
        
        alyr = add_col(aspect, 'aspect', "TEXT", "15")
        
        cursor = arcpy.UpdateCursor(alyr)
        for lnh in cursor:
            __val = int(lnh.getValue("Value"))
            
            lnh.setValue('aspect', d[__val])
            
            cursor.updateRow(lnh)
        
        del cursor, lnh
    
    else:
        asp.save(aspect)
    
    return aspect, asp


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
    Inverso do indice Topografico
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

