"""
Data Extraction tools
"""


def sel_by_attr(inShp, sql, outShp, geomType="area", lyrN=1, api_gis='ogr',
                oEPSG=None, iEPSG=None):
    """
    Select vectorial file and export to new file
    
    If api_gis == 'grass' or 'pygrass', sql is not a query but the where clause
    
    API's Available:
    * ogr;
    * grass;
    * pygrass
    """
    
    if api_gis == 'ogr':
        from glass.pys             import execmd
        from glass.geo.prop.df import drv_name
    
        out_driver = drv_name(outShp)
    
        cmd = (
            'ogr2ogr -f "{drv}" {o} {i} -dialect sqlite -sql "{s}"'
            '{srs}'
        ).format(
            o=outShp, i=inShp, s=sql, drv=out_driver,
            srs=" -s_srs EPSG:{} -t_srs EPSG:{}".format(
                str(iEPSG), str(oEPSG)
            ) if oEPSG and iEPSG else ""
        )
    
        # Execute command
        outcmd = execmd(cmd)
    
    elif api_gis == 'pygrass':
        """
        v.extract via pygrass
        """
        
        from grass.pygrass.modules import Module
        
        m = Module(
            "v.extract", input=inShp, type=geomType, layer=lyrN,
            where=sql, output=outShp, overwrite=True,
            run_=False, quiet=True
        )
        
        m()
    
    elif api_gis == 'grass':
        """
        v.extract via command shell
        """
        
        from glass.pys  import execmd
        
        rcmd = execmd((
            "v.extract input={} type={} layer={} where={} "
            "output={} --overwrite --quiet"
        ).format(inShp, geomType, str(lyrN), sql, outShp))
    
    else:
        raise ValueError('API {} is not available'.format(api_gis))
    
    return outShp


def split_shp_by_attr(inShp, attr, outDir, _format='.shp'):
    """
    Create a new shapefile for each value in a column
    """
    
    import os
    from glass.dct.geo.fmshp   import shp_to_obj
    from glass.pys.oss    import fprop
    from glass.dp.pd.fld import col_distinct
    from glass.dct.geo.toshp   import df_to_shp
    
    # Sanitize format
    FFF = _format if _format[0] == '.' else '.' + _format
    
    # SHP TO DF
    dataDf = shp_to_obj(inShp)
    
    # Get values in attr
    uniqueAttr = col_distinct(dataDf, attr)
    
    # Export Features with the same value in attr to a new File
    BASENAME = fprop(inShp, 'fn', forceLower=True)
    SHPS_RESULT = {}
    i = 1
    for val in uniqueAttr:
        df = dataDf[dataDf[attr] == val]
        
        newShp = df_to_shp(df, os.path.join(outDir, "{}_{}{}".format(
            BASENAME, str(i), FFF
        )))
        
        SHPS_RESULT[val] = newShp
        
        i += 1
    
    return SHPS_RESULT


def sel_by_loc(shp, boundary_filter, filtered_output):
    """
    Filter a shp using the location of a boundary_filter shp
    
    For now the boundary must have only one feature
    
    Writes the filter on a new shp
    """
    
    import os; from osgeo      import ogr
    from glass.geo.prop.df     import drv_name
    from glass.geo.prop.feat   import get_gtype
    from glass.geo.obj.lyr.fld import copy_flds
    from glass.geo.df.cp       import copy_feat
    from glass.pys.oss         import fprop
    
    # Open main data
    dtSrc = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    lyr = dtSrc.GetLayer()
    
    # Get filter geom
    filter_shp = ogr.GetDriverByName(
        drv_name(boundary_filter)).Open(boundary_filter, 0)
    filter_lyr = filter_shp.GetLayer()
    
    c = 0
    for f in filter_lyr:
        if c:
            break
        geom = f.GetGeometryRef()
        c += 1
    
    filter_shp.Destroy()
    
    # Apply filter
    lyr.SetSpatialFilter(geom)
    
    # Copy filter objects to a new shape
    out = ogr.GetDriverByName(
        drv_name(filtered_output)).CreateDataSource(filtered_output)
    
    outLyr  = out.CreateLayer(
        fprop(filtered_output, 'fn'),
        geom_type=get_gtype(shp, gisApi='ogr', name=None, py_cls=True)
    )
    
    # Copy fields
    copy_flds(lyr, outLyr)
    
    copy_feat(
        lyr, outLyr,
        outDefn=outLyr.GetLayerDefn(), only_geom=False, gisApi='ogrlyr'
    )


def geom_by_idx(inShp, idx):
    """
    Get Geometry by index in file
    """
    
    from osgeo           import ogr
    from glass.geo.prop.df import drv_name
    
    src = ogr.GetDriverByName(drv_name(inShp)).Open(inShp)
    lyr = src.GetLayer()
    
    c = 0
    geom = None
    for f in lyr:
        if idx == c:
            geom = f.GetGeometryRef()
        
        else:
            c += 1
    
    if not geom:
        raise ValueError("inShp has not idx")
    
    _geom = geom.ExportToWkt()
    
    del lyr
    src.Destroy()
    
    return _geom


def get_attr_values_in_location(inShp, attr, geomFilter=None, shpFilter=None):
    """
    Get attributes of the features of inShp that intersects with geomFilter
    or shpFilter
    """
    
    from osgeo           import ogr
    from glass.geo.prop.df import drv_name
    
    if not geomFilter and not shpFilter:
        raise ValueError(
            'A geom object or a path to a sho file should be given'
        )
    
    if shpFilter:
        # For now the shpFilter must have only one feature
        filter_shp = ogr.GetDriverByName(
            drv_name(shpFilter)).Open(shpFilter, 0)
        
        filter_lyr = filter_shp.GetLayer()
        c= 0
        for f in filter_lyr:
            if c:
                break
            
            geom = f.GetGeometryRef()
            c += 1
        
        filter_shp.Destroy()
    
    else:
        geom = geomFilter
    
    # Open Main data
    dtSrc = ogr.GetDriverByName(drv_name(inShp)).Open(inShp, 0)
    lyr = dtSrc.GetLayer()
    
    lyr.SetSpatialFilter(geom)
    
    # Get attribute values
    ATTRIBUTE_VAL = [feat.GetField(attr) for feat in lyr]
    
    dtSrc.Destroy()
    
    return ATTRIBUTE_VAL


def split_whr_attrIsTrue(osm_fc, outputfolder, fields=None, sel_fields=None,
                         basename=None):
    """
    For each field in osm table or in fields, creates a new feature class 
    where the field attribute is not empty
    """

    import os
    from glass.geo.prop.feat import lst_fld
    from glass.geo.df.filter      import sel_by_attr

    # List table fields
    tbl_fields = fields if fields else lst_fld(osm_fc)

    if type(tbl_fields) == str:
        tbl_fields = [tbl_fields]

    if sel_fields:
        sel_fields.append('geometry')
        aux = 1

    else:
        aux = 0

    # Export each field in data
    outFilename = '{}.shp' if not basename else basename + '_{}.shp'
    for fld in tbl_fields:
        a = 0
        if not aux:
            sel_fields = ['geometry', fld]
        else:
            if fld not in sel_fields:
                sel_fields.append(fld)
                a += 1

        sel_by_attr(
            osm_fc,
            "SELECT {flds} FROM {t} WHERE {f}<>''".format(
                f=fld, t=os.path.splitext(os.path.basename(osm_fc))[0],
                flds=', '.join(sel_fields)
                ),
            os.path.join(
                outputfolder,
                outFilename.format(fld if fld.islower() else fld.lower())
            ), api_gis='ogr'
        )

        if a:
            sel_fields.remove(fld)

