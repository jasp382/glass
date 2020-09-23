"""
Python data to SHP
"""

def df_to_shp(indf, outShp):
    """
    Pandas Dataframe to ESRI Shapefile
    """
    
    import geopandas
    
    indf.to_file(outShp)
    
    return outShp


def obj_to_shp(dd, geomkey, srs, outshp):
    from glass.geo.obj.pd import df_to_geodf as obj_to_geodf
    
    geodf = obj_to_geodf(dd, geomkey, srs)
    
    return df_to_shp(geodf, outshp)


def eachfeat_to_newshp(inShp, outFolder, epsg=None, idCol=None):
    """
    Export each feature in inShp to a new/single File
    """
    
    import os; from osgeo  import ogr
    from glass.geo.prop.df   import drv_name
    from glass.geo.prop.feat import get_gtype, lst_fld
    from glass.geo.obj.lyr.fld   import copy_flds
    from glass.pys.oss      import fprop
    
    inDt = ogr.GetDriverByName(
        drv_name(inShp)).Open(inShp)
    
    lyr = inDt.GetLayer()
    
    # Get SRS for the output
    if not epsg:
        from glass.geo.prop.prj import get_shp_sref
        srs = get_shp_sref(lyr)
    
    else:
        from glass.geo.prop.prj import get_sref_from_epsg
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


"""
Copy Features
"""

def copy_insame_vector(inShp, colToBePopulated, srcColumn, destinyLayer,
                       geomType="point,line,boundary,centroid",
                       asCMD=None):
    """
    Copy Field values from one layer to another in the same GRASS Vector
    """
    
    if not asCMD:
        from grass.pygrass.modules import Module
        
        vtodb = Module(
            "v.to.db", map=inShp, layer=destinyLayer, type=geomType,
            option="query", columns=colToBePopulated,
            query_column=srcColumn, run_=False, quiet=True
        )
    
        vtodb()
    
    else:
        from glass.pys  import execmd
        
        rcmd = execmd((
            "v.to.db map={} layer={} type={} option=query columns={} "
            "query_column={} --quiet"
        ).format(inShp, destinyLayer, geomType, colToBePopulated,
                 srcColumn))


"""
Excel to SHP
"""

def pointXls_to_shp(xlsFile, outShp, x_col, y_col, epsg, sheet=None):
    """
    Excel table with Point information to ESRI Shapefile
    """
    
    from glass.dct           import tbl_to_obj
    from glass.geo.obj.pd    import pnt_dfwxy_to_geodf
    from glass.dct.geo.toshp import df_to_shp
    
    # XLS TO PANDAS DATAFRAME
    dataDf = tbl_to_obj(xlsFile, sheet=sheet)
    
    # DATAFRAME TO GEO DATAFRAME
    geoDataDf = pnt_dfwxy_to_geodf(dataDf, x_col, y_col, epsg)
    
    # GEODATAFRAME TO ESRI SHAPEFILE
    df_to_shp(geoDataDf, outShp)
    
    return outShp

