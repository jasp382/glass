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
        from glass.pys     import execmd
        from glass.prop.df import drv_name
    
        drv = drv_name(outShp)

        srs = f" -s_srs EPSG:{str(iEPSG)} -t_srs EPSG:{str(oEPSG)}" \
            if oEPSG and iEPSG else ""
    
        cmd = (
            f'ogr2ogr -f "{drv}" {outShp} {inShp} -dialect sqlite '
            f'-sql "{sql}"{srs}'
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
        
        from glass.pys import execmd
        
        rcmd = execmd((
            f"v.extract input={inShp} type={geomType} layer={str(lyrN)} "
            f"where={sql} output={outShp} --overwrite --quiet"
        ))
    
    elif api_gis == 'qgis':
        """
        Use native:extractbyexpression available on QGIS
        """

        from qgis import processing

        params = {
            'INPUT'      : inShp,
            'EXPRESSION' : sql,
            'OUTPUT'     : outShp
        }

        processing.run("native:extractbyexpression", params)
    
    else:
        raise ValueError(f'API {api_gis} is not available')
    
    return outShp


def sel_by_loc(shp, boundary_filter, filtered_output):
    """
    Filter a shp using the location of a boundary_filter shp
    
    For now the boundary must have only one feature
    
    Writes the filter on a new shp
    """
    
    from osgeo           import ogr
    from glass.prop.df   import drv_name
    from glass.prop.feat import get_gtype
    from glass.lyr.fld   import copy_flds
    from glass.dtt.cp    import copy_feat
    from glass.pys.oss   import fprop
    
    # Open main data
    dtSrc = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
    lyr = dtSrc.GetLayer()
    
    # Get filter geom
    filter_shp = ogr.GetDriverByName(
        drv_name(boundary_filter)).Open(boundary_filter, 0)
    filter_lyr = filter_shp.GetLayer()
    
    c = 0
    for f in filter_lyr:
        if c: break

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
    
    from osgeo         import ogr
    from glass.prop.df import drv_name
    
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
    
    from osgeo         import ogr
    from glass.prop.df import drv_name
    
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
    from glass.prop.feat import lst_fld
    from glass.dtt.filter      import sel_by_attr

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

