"""
Splitting with OGR
"""


def splitShp_by_range(shp, nrFeat, outFolder):
    """
    Split one feature class by range
    """
    
    import os
    from glass.pys.oss     import fprop
    from glass.g.prop.feat import feat_count, lst_fld
    from glass.g.tbl.filter    import sel_by_attr
    
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


def eachfeat_to_newshp(inShp, outFolder, epsg=None, idCol=None):
    """
    Export each feature in inShp to a new/single File
    """
    
    import os; from osgeo  import ogr
    from glass.g.prop      import drv_name
    from glass.g.prop.feat import get_gtype, lst_fld
    from glass.g.lyr.fld   import copy_flds
    from glass.pys.oss     import fprop
    
    inDt = ogr.GetDriverByName(
        drv_name(inShp)).Open(inShp)
    
    lyr = inDt.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.g.prop.prj import get_shp_sref
        srs = get_shp_sref(lyr)
    
    else:
        from glass.g.prop.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Get fields name
    fields = lst_fld(lyr)
    
    # Get Geometry type
    geomCls = get_gtype(inShp, gisApi='ogr', name=None, py_cls=True)
    
    # Read features and create a new file for each feature
    RESULT_SHP = []
    for feat in lyr:
        # Create output
        ff = fprop(inShp, ['fn', 'ff'])
        newShp = os.path.join(outFolder, "{}_{}{}".format(
            ff['filename'],
            str(feat.GetFID()) if not idCol else str(feat.GetField(idCol)),
            ff['fileformat']
        ))
        
        newData = ogr.GetDriverByName(
            drv_name(newShp)).CreateDataSource(newShp)
        
        newLyr = newData.CreateLayer(
            fprop(newShp, 'fn'), srs, geom_type=geomCls
        )
        
        # Copy fields from input to output
        copy_flds(lyr, newLyr)
        
        newLyrDefn = newLyr.GetLayerDefn()
        
        # Create new feature
        newFeat = ogr.Feature(newLyrDefn)
        
        # Copy geometry
        geom = feat.GetGeometryRef()
        newFeat.SetGeometry(geom)
        
        # Set fields attributes
        for fld in fields:
            newFeat.SetField(fld, feat.GetField(fld))
        
        # Save feature
        newLyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
        
        del newLyr
        newData.Destroy()
        RESULT_SHP.append(newShp)
    
    return RESULT_SHP


def shpcols_to_shp(inshp, tbl, col_cols, outcolname, outfolder):
    """
    Read a table with a list of columns in a shapefile

    For each column:
    in the input shapefile, delete all other columns
    rename the column, and save the changed shapefile

    explain why col_cols could be a list
    """

    import os
    from glass.pys import obj_to_lst
    from glass.g.rd.shp import shp_to_obj
    from glass.ng.rd    import tbl_to_obj
    from glass.g.wt.shp import df_to_shp

    dfshp = shp_to_obj(inshp)
    dfcols = tbl_to_obj(tbl)

    col_cols = obj_to_lst(col_cols)

    refcols = []
    for cc in col_cols:
        refcols.extend(dfcols[cc].tolist())

    for i, r in dfcols.iterrows():
        for cc in col_cols:
            newdf = dfshp.copy()

            dc = [c for c in refcols if c != r[cc]]

            if outcolname in list(newdf.columns.values):
                dc.append(outcolname)

            newdf.drop(dc, axis=1, inplace=True)

            newdf.rename(columns={
                r[cc] : outcolname
            }, inplace=True)

            df_to_shp(newdf, os.path.join(outfolder, r[cc] + '.shp'))
    
    return outfolder

