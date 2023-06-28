"""
Splitting with OGR
"""

import os

from glass.pys.oss import fprop


def splitShp_by_range(shp, nrFeat, outFolder):
    """
    Split one feature class by range
    """
    
    from glass.prop.feat  import feat_count, lst_fld
    from glass.tbl.filter import sel_by_attr
    
    rowsN = feat_count(shp, gisApi='ogr')
    
    nrShp = int(rowsN / float(nrFeat)) + 1 if nrFeat != rowsN else 1
    
    fields = lst_fld(shp)
    
    offset = 0
    exportedShp = []
    for i in range(nrShp):
        f = fprop(shp, ['fn', 'ff'], forceLower=True)

        fn, ff = f['filename'], f['fileformat']

        cols = ', '.join(fields)

        q = (
            f"SELECT {cols}, geometry "
            f"FROM {fn} "
            f"ORDER BY {cols} "
            f"LIMIT {str(nrFeat)} OFFSET {str(offset)}"
        )
        
        outShp = sel_by_attr(
            shp, q,
            os.path.join(outFolder, f"{fn}_{str(i)}{ff}"),
            api_gis='ogr'
        )
        
        exportedShp.append(outShp)
        offset += nrFeat
    
    return exportedShp


def eachfeat_to_newshp(inShp, outFolder, epsg=None, idCol=None, idIsName=None):
    """
    Export each feature in inShp to a new/single File
    """
    
    from osgeo           import ogr
    from glass.prop      import drv_name
    from glass.prop.feat import get_gtype, lst_fld
    from glass.lyr.fld   import copy_flds
    
    inDt = ogr.GetDriverByName(
        drv_name(inShp)).Open(inShp)
    
    lyr = inDt.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.prop.prj import get_shp_sref
        srs = get_shp_sref(lyr)
    
    else:
        from glass.prop.prj import get_sref_from_epsg
        srs = get_sref_from_epsg(epsg)
    
    # Get fields name
    fields = lst_fld(lyr)
    
    # Get Geometry type
    geomCls = get_gtype(inShp, gisApi='ogr', name=None, py_cls=True)
    
    # Read features and create a new file for each feature
    res_shp = []
    for feat in lyr:
        # Create output
        ff = fprop(inShp, ['fn', 'ff'])
        fname, ffmt = ff['filename'], ff['fileformat']

        if idIsName and idCol:
            shpname = f"{str(feat.GetField(idCol))}{ffmt}"

        else:
            fid = str(feat.GetFID()) if not idCol else str(feat.GetField(idCol))
            shpname = f"{fname}_{fid}{ffmt}"

        newShp = os.path.join(outFolder, shpname)
        
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

        if newShp not in res_shp:
            res_shp.append(newShp)
    
    return res_shp


def shpcols_to_shp(inshp, tbl, col_cols, outcolname, outfolder):
    """
    Read a table with a list of columns in a shapefile

    For each column:
    in the input shapefile, delete all other columns
    rename the column, and save the changed shapefile

    explain why col_cols could be a list
    """

    from glass.pys    import obj_to_lst
    from glass.rd.shp import shp_to_obj
    from glass.rd     import tbl_to_obj
    from glass.wt.shp import df_to_shp

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



def split_shp_by_attr(inShp, attr, outDir, _format='.shp', outname=None, valinname=None):
    """
    Create a new shapefile for each value in a column
    """
    
    from glass.rd.shp  import shp_to_obj
    from glass.pd.fld  import col_distinct
    from glass.wt.shp  import df_to_shp
    
    # Sanitize format
    FFF = _format if _format[0] == '.' else '.' + _format
    
    # SHP TO DF
    dataDf = shp_to_obj(inShp)
    
    # Get values in attr
    uniqueAttr = col_distinct(dataDf, attr)
    
    # Export Features with the same value in attr to a new File
    bname = fprop(inShp, 'fn', forceLower=True) if not outname else outname
    shps_res = {}
    i = 1
    for val in uniqueAttr:
        df = dataDf[dataDf[attr] == val]
        
        fid = str(i) if not valinname else str(val)
        newShp = df_to_shp(df, os.path.join(
            outDir, f"{bname}_{fid}{FFF}"
        ))
        
        shps_res[val] = newShp
        
        i += 1
    
    return shps_res

