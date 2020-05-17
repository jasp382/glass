"""
OpenStreetMap to Land Use/Land Cover Maps
"""


def raster_based(osmdata, nomenclature, refRaster, lulcRst,
                 overwrite=None, dataStore=None, roadsAPI='POSTGIS'):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An raster based approach.
    
    TODO: Add detailed description
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import datetime; import os; import pandas; import copy
    # ************************************************************************ #
    # Gasp dependencies #
    # ************************************************************************ #
    from glass.pyt.oss               import mkdir, fprop
    from glass.geo.gt.prop.ff        import check_isRaster
    from glass.geo.gt.prop.prj       import get_rst_epsg
    from glass.geo.wenv.grs          import run_grass
    if roadsAPI == 'POSTGIS':
        from glass.sql.db            import create_db
        from glass.geo.gql.to.osm    import osm_to_psql 
        from glass.geo.osm2lulc.mod2 import roads_sqdb
        from glass.sql.fm            import dump_db
        from glass.sql.db            import drop_db
    else:
        from glass.geo.gt.toshp.osm  import osm_to_sqdb
        from glass.geo.osm2lulc.mod2 import grs_rst_roads
    from glass.geo.osm2lulc.utils    import osm_project, add_lulc_to_osmfeat, osmlulc_rsttbl
    from glass.geo.osm2lulc.utils    import get_ref_raster
    from glass.geo.osm2lulc.mod1     import grs_rst
    from glass.geo.osm2lulc.m3_4     import rst_area
    from glass.geo.osm2lulc.mod5     import basic_buffer
    from glass.geo.osm2lulc.mod6     import rst_pnt_to_build
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    # Check if input parameters exists!
    if not os.path.exists(os.path.dirname(lulcRst)):
        raise ValueError('{} does not exist!'.format(os.path.dirname(lulcRst)))
    
    if not os.path.exists(osmdata):
        raise ValueError('File with OSM DATA ({}) does not exist!'.format(osmdata))
    
    if not os.path.exists(refRaster):
        raise ValueError('File with reference area ({}) does not exist!'.format(refRaster))
    
    # Check if Nomenclature is valid
    nomenclature = "URBAN_ATLAS" if nomenclature != "URBAN_ATLAS" and \
        nomenclature != "CORINE_LAND_COVER" and \
        nomenclature == "GLOBE_LAND_30" else nomenclature
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    
    workspace = os.path.join(os.path.dirname(
        lulcRst), 'osmtolulc') if not dataStore else dataStore
    
    # Check if workspace exists
    if os.path.exists(workspace):
        if overwrite:
            mkdir(workspace)
        else:
            raise ValueError('Path {} already exists'.format(workspace))
    else:
        mkdir(workspace)
    
    # Get Ref Raster
    refRaster, epsg = get_ref_raster(refRaster, workspace, cellsize=2)
    
    from glass.geo.osm2lulc import PRIORITIES, osmTableData, LEGEND
    
    __priorites = PRIORITIES[nomenclature]
    __legend    = LEGEND[nomenclature]
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB or to POSTGIS DB #
    # ************************************************************************ #
    if roadsAPI == 'POSTGIS':
        osm_db = create_db(fprop(
            osmdata, 'fn', forceLower=True), overwrite=True)
        osm_db = osm_to_psql(osmdata, osm_db)
    else:
        osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    time_c = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature, api=roadsAPI)
    time_d = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(
        osm_db, epsg, api=roadsAPI,
        isGlobeLand=None if nomenclature != 'GLOBE_LAND_30' else True
    )
    time_e = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    grass_base = run_grass(
        workspace, grassBIN='grass78', location='grloc', srs=epsg)
    import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, workspace, 'grloc', 'PERMANENT')
    
    # ************************************************************************ #
    # IMPORT SOME GASP MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from glass.geo.gt.torst   import rst_to_grs, grs_to_rst
    from glass.geo.gt.nop.mos import rsts_to_mosaic
    from glass.geo.wenv.grs   import rst_to_region
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(refRaster, 'extent_raster')
    rst_to_region(extRst)
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # MapResults #
    mergeOut = {}
    # ************************************************************************ #
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    """
    selOut = {
        cls_code : rst_name, ...
    }
    """
    selOut, timeCheck1 = grs_rst(osm_db, osmTableData['polygons'], api=roadsAPI)

    for cls in selOut:
        mergeOut[cls] = [selOut[cls]]
    
    time_g = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    """
    roads = {
        cls_code : rst_name, ...
    }
    """
    
    if roadsAPI != 'POSTGIS':
        roads, timeCheck2 = grs_rst_roads(
            osm_db, osmTableData['lines'], osmTableData['polygons'],
            workspace, 1221 if nomenclature != "GLOBE_LAND_30" else 801
        )
    else:
        roadCls = 1221 if nomenclature != "GLOBE_LAND_30" else 801
        
        roads, timeCheck2 = roads_sqdb(
            osm_db, osmTableData['lines'], osmTableData['polygons'],
            apidb='POSTGIS', asRst=roadCls
        )
        
        roads = {roadCls : roads}
    
    for cls in roads:
        if cls not in mergeOut:
            mergeOut[cls] = [roads[cls]]
        else:
            mergeOut[cls].append(roads[cls])
    
    time_h = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    """
    auOut = {
        cls_code : rst_name, ...
    }
    """
    
    if nomenclature != 'GLOBE_LAND_30':
        auOut, timeCheck3 = rst_area(
            osm_db, osmTableData['polygons'], UPPER=True, api=roadsAPI
        )
        
        for cls in auOut:
            if cls not in mergeOut:
                mergeOut[cls] = [auOut[cls]]
            else:
                mergeOut[cls].append(auOut[cls])
    
        time_l = datetime.datetime.now().replace(microsecond=0)
    else:
        timeCheck3 = None
        time_l     = None
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    """
    alOut = {
        cls_code : rst_name, ...
    }
    """
    if nomenclature != 'GLOBE_LAND_30':
        alOut, timeCheck4 = rst_area(
            osm_db, osmTableData['polygons'], UPPER=None, api=roadsAPI
        )
        for cls in alOut:
            if cls not in mergeOut:
                mergeOut[cls] = [alOut[cls]]
            else:
                mergeOut[cls].append(alOut[cls])
    
        time_j = datetime.datetime.now().replace(microsecond=0)
    else:
        timeCheck4 = None
        time_j     = None
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    """
    bfOut = {
        cls_code : rst_name, ...
    }
    """
    
    bfOut, timeCheck5 = basic_buffer(
        osm_db, osmTableData['lines'], workspace, apidb=roadsAPI
    )
    for cls in bfOut:
        if cls not in mergeOut:
            mergeOut[cls] = [bfOut[cls]]
        else:
            mergeOut[cls].append(bfOut[cls])
    
    time_m = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 7 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        buildsOut, timeCheck7 = rst_pnt_to_build(
            osm_db, osmTableData['points'], osmTableData['polygons'],
            api_db=roadsAPI
        )
        
        for cls in buildsOut:
            if cls not in mergeOut:
                mergeOut[cls] = buildsOut[cls]
            else:
                mergeOut[cls] += buildsOut[cls]
        
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    else:
        timeCheck7 = None
        time_n = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Merge all results for one cls into one raster
    mergeOut = {
        cls_code : [rst_name, rst_name, ...], ...
    }
    into
    mergeOut = {
        cls_code : patched_raster, ...
    }
    """
    
    for cls in mergeOut:
        if len(mergeOut[cls]) == 1:
            mergeOut[cls] = mergeOut[cls][0]
        
        else:
            mergeOut[cls] = rsts_to_mosaic(
                mergeOut[cls], 'mosaic_{}'.format(str(cls)), api="grass"
            )
    
    time_o = datetime.datetime.now().replace(microsecond=0)
    
    """
    Merge all Class Raster using a priority rule
    """
    
    __priorities = PRIORITIES[nomenclature]
    lst_rst = []
    for cls in __priorities:
        if cls not in mergeOut:
            continue
        else:
            lst_rst.append(mergeOut[cls])
    
    outGrs = rsts_to_mosaic(lst_rst, os.path.splitext(
        os.path.basename(lulcRst))[0], api="grass"
    )
    time_p = datetime.datetime.now().replace(microsecond=0)
    
    # Ceck if lulc Rst has an valid format
    outIsRst = check_isRaster(lulcRst)
    if not outIsRst:
        from glass.pyt.oss import fprop
        lulcRst = os.path.join(
            os.path.dirname(lulcRst),
            fprop(lulcRst, 'fn') + '.tif'
        )
    
    grs_to_rst(outGrs, lulcRst, as_cmd=True)
    osmlulc_rsttbl(nomenclature, os.path.join(
        os.path.dirname(lulcRst), os.path.basename(lulcRst) + '.vat.dbf'
    ))
    
    time_q = datetime.datetime.now().replace(microsecond=0)

    # Dump Database if PostGIS was used
    # Drop Database if PostGIS was used
    if roadsAPI == 'POSTGIS':
        dump_db(osm_db, os.path.join(
            workspace, osm_db + '.sql'
        ), api='psql')
        drop_db(osm_db)
    
    return lulcRst, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('set_grass', time_f - time_e),
        5  : ('rule_1', time_g - time_f, timeCheck1),
        6  : ('rule_2', time_h - time_g, timeCheck2),
        7  : None if not timeCheck3 else ('rule_3', time_l - time_h, timeCheck3),
        8  : None if not timeCheck4 else ('rule_4', time_j - time_l, timeCheck4),
        9  : ('rule_5', time_m - time_j if timeCheck4 else time_m - time_h, timeCheck5),
        10 : None if not timeCheck7 else ('rule_7', time_n - time_m, timeCheck7),
        11 : ('merge_rst', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('export_rst', time_q - time_p)
    }

# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #

def vector_based(osmdata, nomenclature, refRaster, lulcShp,
                 overwrite=None, dataStore=None, RoadsAPI='POSTGIS'):
    """
    Convert OSM Data into Land Use/Land Cover Information
    
    An vector based approach.
    
    TODO: Add a detailed description.
    
    RoadsAPI Options:
    * GRASS
    * SQLITE
    * POSTGIS
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import datetime; import os; import copy
    # ************************************************************************ #
    # GASP dependencies #
    # ************************************************************************ #
    from glass.pyt.oss               import fprop, mkdir
    from glass.geo.wenv.grs          import run_grass
    if RoadsAPI == 'POSTGIS':
        from glass.sql.db            import create_db
        from glass.geo.gql.to.osm    import osm_to_psql
        from glass.sql.db            import drop_db
        from glass.sql.fm            import dump_db
    else:
        from glass.geo.gt.toshp.osm  import osm_to_sqdb
    from glass.geo.osm2lulc.utils    import osm_project, add_lulc_to_osmfeat, get_ref_raster
    from glass.geo.gt.toshp.mtos     import shps_to_shp
    from glass.geo.osm2lulc.mod1     import grs_vector
    if RoadsAPI == 'SQLITE' or RoadsAPI == 'POSTGIS':
        from glass.geo.osm2lulc.mod2 import roads_sqdb
    else:
        from glass.geo.osm2lulc.mod2 import grs_vec_roads
    from glass.geo.osm2lulc.m3_4     import grs_vect_selbyarea
    from glass.geo.osm2lulc.mod5     import grs_vect_bbuffer
    from glass.geo.osm2lulc.mod6     import vector_assign_pntags_to_build
    from glass.geo.gt.toshp.mtos     import same_attr_to_shp
    from glass.geo.gt.prj            import def_prj
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    # Check if input parameters exists!
    if not os.path.exists(os.path.dirname(lulcShp)):
        raise ValueError('{} does not exist!'.format(os.path.dirname(lulcShp)))
    
    if not os.path.exists(osmdata):
        raise ValueError('File with OSM DATA ({}) does not exist!'.format(osmdata))
    
    if not os.path.exists(refRaster):
        raise ValueError('File with reference area ({}) does not exist!'.format(refRaster))
    
    # Check if Nomenclature is valid
    nomenclature = "URBAN_ATLAS" if nomenclature != "URBAN_ATLAS" and \
        nomenclature != "CORINE_LAND_COVER" and \
        nomenclature == "GLOBE_LAND_30" else nomenclature
    
    time_a = datetime.datetime.now().replace(microsecond=0)
    
    # Create workspace for temporary files
    workspace = os.path.join(os.path.dirname(
        lulcShp), 'osmtolulc') if not dataStore else dataStore
    
    # Check if workspace exists
    if os.path.exists(workspace):
        if overwrite:
            mkdir(workspace)
        else:
            raise ValueError('Path {} already exists'.format(workspace))
    else:
        mkdir(workspace)
    
    # Get Reference Raster
    refRaster, epsg = get_ref_raster(refRaster, workspace, cellsize=10)
    
    from glass.geo.osm2lulc import osmTableData, PRIORITIES, LEGEND
    
    __priorities = PRIORITIES[nomenclature]
    __legend     = LEGEND[nomenclature]
    
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if RoadsAPI != 'POSTGIS':
        # ******************************************************************** #
        # Convert OSM file to SQLITE DB #
        # ******************************************************************** #
        osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    else:
        # Convert OSM file to POSTGRESQL DB #
        osm_db = create_db(fprop(
            osmdata, 'fn', forceLower=True), overwrite=True)
        osm_db = osm_to_psql(osmdata, osm_db)
    time_c = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(
        osm_db, osmTableData, nomenclature,
        api='SQLITE' if RoadsAPI != 'POSTGIS' else RoadsAPI
    )
    time_d = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(
        osm_db, epsg,
        api='SQLITE' if RoadsAPI != 'POSTGIS' else RoadsAPI,
        isGlobeLand=None if nomenclature != 'GLOBE_LAND_30' else True
    )
    time_e = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    grass_base = run_grass(workspace, grassBIN='grass78', location='grloc', srs=epsg)
    #import grass.script as grass
    import grass.script.setup as gsetup
    gsetup.init(grass_base, workspace, 'grloc', 'PERMANENT')
    
    # ************************************************************************ #
    # IMPORT SOME GASP MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from glass.geo.gt.gop.ovlay import erase
    from glass.geo.wenv.grs     import rst_to_region
    from glass.geo.gt.gop.genze import dissolve
    from glass.geo.gt.tbl.grs   import add_and_update, reset_table, update_table
    from glass.geo.gt.tbl.fld   import add_fields
    from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
    from glass.geo.gt.torst     import rst_to_grs
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(refRaster, 'extent_raster')
    rst_to_region(extRst)
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    osmShps = []
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    ruleOneShp, timeCheck1 = grs_vector(
        osm_db, osmTableData['polygons'], apidb=RoadsAPI
    )
    osmShps.append(ruleOneShp)
    
    time_g = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    ruleRowShp, timeCheck2 = roads_sqdb(
        osm_db, osmTableData['lines'], osmTableData['polygons'], apidb=RoadsAPI
    ) if RoadsAPI == 'SQLITE' or RoadsAPI == 'POSTGIS' else grs_vec_roads(
        osm_db, osmTableData['lines'], osmTableData['polygons'])
    
    osmShps.append(ruleRowShp)
    time_h = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        ruleThreeShp, timeCheck3 = grs_vect_selbyarea(
            osm_db, osmTableData['polygons'], UPPER=True, apidb=RoadsAPI
        )
    
        osmShps.append(ruleThreeShp)
        time_l = datetime.datetime.now().replace(microsecond=0)
    else:
        timeCheck3 = None
        time_l     = None
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        ruleFourShp, timeCheck4 = grs_vect_selbyarea(
            osm_db, osmTableData['polygons'], UPPER=False, apidb=RoadsAPI
        )
    
        osmShps.append(ruleFourShp)
        time_j = datetime.datetime.now().replace(microsecond=0)
    else:
        timeCheck4 = None
        time_j     = None
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    ruleFiveShp, timeCheck5 = grs_vect_bbuffer(
        osm_db, osmTableData["lines"], api_db=RoadsAPI
    )
    
    osmShps.append(ruleFiveShp)
    time_m = datetime.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 7 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nomenclature != "GLOBE_LAND_30":
        ruleSeven11, ruleSeven12, timeCheck7 = vector_assign_pntags_to_build(
            osm_db, osmTableData['points'], osmTableData['polygons'],
            apidb=RoadsAPI
        )
        
        if ruleSeven11:
            osmShps.append(ruleSeven11)
        
        if ruleSeven12:
            osmShps.append(ruleSeven12)
        
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    else:
        timeCheck7 = None
        time_n = datetime.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Get Shps with all geometries related with one class - One Shape for Classe
    """
    
    _osmShps = []
    for i in range(len(osmShps)):
        if not osmShps[i]: continue
        
        _osmShps.append(grs_to_shp(
            osmShps[i], os.path.join(workspace, osmShps[i] + '.shp'),
            'auto', lyrN=1, asCMD=True, asMultiPart=None
        ))
    
    for shp in _osmShps:
        def_prj(os.path.splitext(shp)[0] + '.prj', epsg=epsg, api='epsgio')
    
    _osmShps = same_attr_to_shp(
        _osmShps, "cat", workspace, "osm_", resultDict=True
    )
    del osmShps
    
    time_o = datetime.datetime.now().replace(microsecond=0)
    
    """
    Merge all Classes into one feature class using a priority rule
    """
    
    osmShps = {}
    for cls in _osmShps:
        if cls == '1':
            osmShps[1221] = shp_to_grs(_osmShps[cls], "osm_1221", asCMD=True)
        
        else:
            osmShps[int(cls)] = shp_to_grs(_osmShps[cls], "osm_" + cls,
                asCMD=True)
    
    # Erase overlapping areas by priority
    osmNameRef = copy.deepcopy(osmShps)
    
    for e in range(len(__priorities)):
        if e + 1 == len(__priorities): break
        
        if __priorities[e] not in osmShps:
            continue
        else:
            for i in range(e+1, len(__priorities)):
                if __priorities[i] not in osmShps:
                    continue
                else:
                    osmShps[__priorities[i]] = erase(
                        osmShps[__priorities[i]], osmShps[__priorities[e]],
                        "{}_{}".format(osmNameRef[__priorities[i]], e),
                        notTbl=True, api='pygrass'
                    )
    
    time_p = datetime.datetime.now().replace(microsecond=0)
    
    # Export all classes
    lst_merge = []
    a = None
    for i in range(len(__priorities)):
        if __priorities[i] not in osmShps:
            continue
        
        if not a:
            reset_table(
                osmShps[__priorities[i]],
                {'cls' : 'varchar(5)', 'leg' : 'varchar(75)'},
                {'cls' : str(__priorities[i]), 'leg' : str(__legend[__priorities[i]])}
            )
            
            a = 1
        
        else:
            add_and_update(
                osmShps[__priorities[i]],
                {'cls' : 'varchar(5)'},
                {'cls' : str(__priorities[i])}
            )
        
        ds = dissolve(
            osmShps[__priorities[i]],
            'dl_{}'.format(str(__priorities[i])), 'cls', api="grass"
        )
        
        add_fields(ds, {'leg': 'varchar(75)'}, api="grass")
        update_table(ds, 'leg', str(__legend[__priorities[i]]), 'leg is null')
        
        lst_merge.append(grs_to_shp(
            ds, os.path.join(
                workspace, "lulc_{}.shp".format(str(__priorities[i]))
            ), 'auto', lyrN=1, asCMD=True, asMultiPart=None
        ))
    
    time_q = datetime.datetime.now().replace(microsecond=0)
    
    if fprop(lulcShp, 'ff') != '.shp':
        lulcShp = os.path.join(
            os.path.dirname(lulcShp), fprop(lulcShp, 'fn') + '.shp')
    
    shps_to_shp(lst_merge, lulcShp, api='pandas')

    # Check if prj of lulcShp exists and create it if necessary
    prj_ff = os.path.splitext(lulcShp)[0] + '.prj'
    if not os.path.exists(prj_ff):
        def_prj(prj_ff, epsg=epsg, api='epsgio')
    
    time_r = datetime.datetime.now().replace(microsecond=0)

    # Dump Database if PostGIS was used
    # Drop Database if PostGIS was used
    if RoadsAPI == 'POSTGIS':
        dump_db(osm_db, os.path.join(
            workspace, osm_db + '.sql'
        ), api='psql')
        drop_db(osm_db)
    
    return lulcShp, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('set_grass', time_f - time_e),
        5  : ('rule_1', time_g - time_f, timeCheck1),
        6  : ('rule_2', time_h - time_g, timeCheck2),
        7  : None if not timeCheck3 else ('rule_3', time_l - time_h, timeCheck3),
        8  : None if not timeCheck4 else ('rule_4', time_j - time_l, timeCheck4),
        9  : ('rule_5',
            time_m - time_j if timeCheck4 else time_m - time_h, timeCheck5),
        10 : None if not timeCheck7 else ('rule_7', time_n - time_m, timeCheck7),
        11 : ('disj_cls', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('export_cls', time_q - time_p),
        14 : ('merge_cls', time_r - time_q)
    }

