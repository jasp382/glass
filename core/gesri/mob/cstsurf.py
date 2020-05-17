"""
Network and Raster
"""

"""
Produce Raster Cost Surfaces with ArcGIS
"""
def acost_surface(mdt, tax_cos, cos, leg_cos, barr, rdv, fldRdv, w, SupCst):
    """
    Tool for make a cost surface based on the roads, slope, land use and
    physical barriers
    """
    
    import arcpy; import os;           import unicodedata
    from glass.cpu.arcg.spanlst.rcls    import reclassify
    from glass.spanlst.surf             import slope
    from glass.spanlst.local            import combine
    from glass.cpu.arcg.spanlst.rcls    import lookup
    from glass.cpu.arcg.mng.fld         import add_field
    from glass.cpu.arcg.mng.fld         import list_fields
    from glass.cpu.arcg.mng.rst.dataset import mosaic_to_raster
    from glass.anls.ovlay               import union
    from glass.to.rst                   import shp_to_raster
    
    def GetRules4Slope():
        r = {1 : [0, 10],
            2 : [10, 30],
            3 : [30, 50],
            4 : [50, 70],
            5 : [70, 100],
            6 : [100, 500]}
        s = [
            "{first} {second} {new_value}".format(
                new_value=str(k), first=str(r[k][0]), second=str(r[k][1])
            ) for k in r.keys()
        ]
        return "; ".join(s)
    
    def GetFldFidBarr(shp):
        filename = str(os.path.basename(shp))
        wext = str.split(filename, ".")[0]
        if len(wext) < 6:
            fld_name = "FID_{c}".format(c=wext)
        else:
            fld_name = "FID_{c}".format(c=wext[:6])
        return fld_name
    
    def GetRulesBarrCos(t, cd):
        taxonomia = LULC_Taxonomia(t, cd)
        lst_cls = []
        lst_cls.extend(taxonomia.keys())
        lst_cls.append('100')
        for i in range(len(lst_cls)):
            if lst_cls[i] == '100' or lst_cls[i] == '6':
                lst_cls[i] = "'{lulc}' NODATA".format(lulc=lst_cls[i])
            else:
                lst_cls[i] = "'{lulc}' {lulc}".format(lulc=lst_cls[i])
        return "; ".join(lst_cls)
    
    def GetRulesRdv(rdv, fld):
        l = ["{v} {v}".format(v=str(lnh.getValue(fld))) for lnh in arcpy.SearchCursor(rdv, "", "", "", "")]
        l.append("NODATA 0")
        return ";".join(l)
    
    def CalcImpedance(rst, t_cos, c):
        taxonomia = LULC_Taxonomia(t_cos, c)
        # Create Field for the output
        AddField(rst, "cst", "FLOAT", "6", "3")
        # List Fields
        fld_lst = ListTableFields(rst)
        cursor = arcpy.UpdateCursor(rst)
        for linha in cursor:
            declv = linha.getValue(fld_lst[4])
            fd = linha.getValue(fld_lst[3])
            if declv == 1:
                w_declv = 1
                if fd >= 6:
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    tmp_wCos = taxonomia[int(fd)]['weight']
            elif declv == 2:
                if fd >= 6:
                    w_declv = 1
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    w_declv = 1.5
                    tmp_wCos = taxonomia[int(fd)]['weight']
            elif declv == 3:
                if fd >= 6:
                    w_declv = 1.5
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    w_declv = 2
                    tmp_wCos = taxonomia[int(fd)]['weight']
            elif declv == 4:
                if fd >= 6:
                    w_declv = 1.5
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    w_declv = 3
                    tmp_wCos = taxonomia[int(fd)]['weight']
            elif declv == 5:
                if fd >= 6:
                    w_declv = 2
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    w_declv = 4
                    tmp_wCos = taxonomia[int(fd)]['weight']
            elif declv == 6:
                if fd >= 6:
                    w_declv = 2
                    tmp_wCos = (3600.0 * 10) / (fd * 1000.0)
                else:
                    w_declv = 5
                    tmp_wCos = taxonomia[int(fd)]['weight']
            linha.setValue("cst", w_declv * tmp_wCos)
            cursor.updateRow(linha)
        return "cst"
    
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = w
    
    # Get Cellsize
    cellsize = str(arcpy.GetRasterProperties_management(mdt, "CELLSIZEX", ""))
    
    """
    Make Cost Surface
    """
    # Create Slope Layer
    declv = slope(mdt, "declv.img", "PERCENT_RISE", api='arcpy')
    # Reclassify Slope Layer
    rcls_declv = Reclassify(declv, "Value", GetRules4Slope(), "rcls_declv.img", mdt)
    # Update LandUse Shapefile
    AddField(cos, "leg", "TEXT", "50")
    cls_cos = LULC_Taxonomia(tax_cos, cellsize)
    up_cursor = arcpy.UpdateCursor(cos); linha = up_cursor.next()
    while linha:
        cls = str(linha.getValue(leg_cos))
        for i in cls_cos.keys():
            for e in cls_cos[i]['cls']:
                if e == cls:
                    up = i
                    break
        linha.setValue("leg", up)
        up_cursor.updateRow(linha)
        linha=up_cursor.next()
    del up_cursor, linha
    # Union Landuse/barreiras
    barrcos = union(barr, cos, "barrcos.shp", gis_api="arcpy")
    # Identify barreiras
    cursor = arcpy.UpdateCursor(barrcos)
    for i in cursor:
        f = int(i.getValue(GetFldFidBarr(barr)))
        if f >= 0:
            i.setValue("leg", "100")
            cursor.updateRow(i)
    del cursor, i
    # BARRCOS to Raster
    rst_barrcos = ShpToRaster(barrcos, "leg", "rst_cos.img", cellsize, mdt)
    # Reclassify BARRCOS
    rcls_barrcos = Reclassify(rst_barrcos, "leg", GetRulesBarrCos(tax_cos, cellsize), "rcls_barrcos.img", mdt)
    # Combine Rdv with BARRCOS
    rst_rdv = ShpToRaster(rdv, fldRdv, "rst_rdv.img", cellsize, mdt)
    # Reclass RDV: NODATA to 0
    rcls_rdv = Reclassify(rst_rdv, fldRdv, GetRulesRdv(rst_rdv, fldRdv), "rcls_rdv.img", mdt)
    # Mosaic to raster (Combine BARRCOS with RDV)
    barrcosrdv = RasterPatch([rcls_barrcos, rcls_rdv], "barrcosrdv.img", w, cellsize, "MAXIMUM", mdt)
    # Reclass RDV: 0 to NODATA
    barrcosrdv = Reclassify(barrcosrdv, "Value", "0 NODATA", "barrcosrdv_v2.img", mdt)
    # Combine BARR/COS/RDV/SLOPE
    combine = combine([barrcosrdv, declv], "combine.img", api='arcpy')
    # Calculate impedance for all combinations of categories
    fld_impedance = CalcImpedance(combine, tax_cos, cellsize)
    return LookupRaster(combine, fld_impedance, SupCst)

# *****************************************************************************#
# *****************************************************************************#
# *****************************************************************************#
"""
Produce Raster Cost Surfaces with ArcGIS
"""
