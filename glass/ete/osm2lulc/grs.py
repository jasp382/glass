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
    import datetime as dt
    import os
    # ************************************************************************ #
    # glass dependencies #
    # ************************************************************************ #
    from glass.pys.oss               import mkdir, fprop
    from glass.prop.df               import is_rst
    from glass.wenv.grs              import run_grass
    if roadsAPI == 'POSTGIS':
        from glass.sql.db            import create_pgdb
        from glass.it.db             import osm_to_psql 
        from glass.ete.osm2lulc.mod2 import roads_sqdb
        from glass.sql.bkup          import dump_db
        from glass.sql.db            import drop_db
    else:
        from glass.it.osm  import osm_to_sqdb
        from glass.ete.osm2lulc.mod2 import grs_rst_roads
    from glass.ete.osm2lulc.utils    import osm_project, add_lulc_to_osmfeat, osmlulc_rsttbl
    from glass.ete.osm2lulc.utils    import get_ref_raster
    from glass.ete.osm2lulc.mod1     import grs_rst
    from glass.ete.osm2lulc.m3_4     import rst_area
    from glass.ete.osm2lulc.mod5     import basic_buffer
    from glass.ete.osm2lulc.mod6     import rst_pnt_to_build
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    # Check if input parameters exists!
    if not os.path.exists(os.path.dirname(lulcRst)):
        raise ValueError(f'{os.path.dirname(lulcRst)} does not exist!')
    
    if not os.path.exists(osmdata):
        raise ValueError(f'File with OSM DATA ({osmdata}) does not exist!')
    
    if not os.path.exists(refRaster):
        raise ValueError(f'File with reference area ({refRaster}) does not exist!')
    
    # Check if Nomenclature is valid
    nomenclature = "URBAN_ATLAS" if nomenclature != "URBAN_ATLAS" and \
        nomenclature != "CORINE_LAND_COVER" and \
        nomenclature == "GLOBE_LAND_30" else nomenclature
    
    time_a = dt.datetime.now().replace(microsecond=0)
    
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
    
    from glass.ete.osm2lulc import PRIORITIES, osmTableData, LEGEND
    
    __priorites = PRIORITIES[nomenclature]
    __legend    = LEGEND[nomenclature]
    time_b = dt.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB or to POSTGIS DB #
    # ************************************************************************ #
    if roadsAPI == 'POSTGIS':
        osm_db = create_pgdb(fprop(
            osmdata, 'fn', forceLower=True), overwrite=True)
        osm_db = osm_to_psql(osmdata, osm_db)
    else:
        osm_db = osm_to_sqdb(osmdata, os.path.join(workspace, 'osm.sqlite'))
    time_c = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    add_lulc_to_osmfeat(osm_db, osmTableData, nomenclature, api=roadsAPI)
    time_d = dt.datetime.now().replace(microsecond=0)
    
    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osmTableData = osm_project(
        osm_db, epsg, api=roadsAPI,
        isGlobeLand=None if nomenclature != 'GLOBE_LAND_30' else True
    )
    time_e = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    grass_base = run_grass(
        workspace, grassBIN='grass78', location='grloc', srs=epsg)
    
    import grass.script.setup as gsetup
    gsetup.init(grass_base, workspace, 'grloc', 'PERMANENT')
    
    # ************************************************************************ #
    # IMPORT SOME glass MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from glass.it.rst   import rst_to_grs, grs_to_rst
    from glass.rst.mos import rsts_to_mosaic
    from glass.wenv.grs   import rst_to_region
    # ************************************************************************ #
    # SET GRASS GIS LOCATION EXTENT #
    # ************************************************************************ #
    extRst = rst_to_grs(refRaster, 'extent_raster')
    rst_to_region(extRst)
    time_f = dt.datetime.now().replace(microsecond=0)
    
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
    
    time_g = dt.datetime.now().replace(microsecond=0)
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
    
    time_h = dt.datetime.now().replace(microsecond=0)
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
    
        time_l = dt.datetime.now().replace(microsecond=0)
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
    
        time_j = dt.datetime.now().replace(microsecond=0)
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
    
    time_m = dt.datetime.now().replace(microsecond=0)
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
        
        time_n = dt.datetime.now().replace(microsecond=0)
    
    else:
        timeCheck7 = None
        time_n = dt.datetime.now().replace(microsecond=0)
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
    
    time_o = dt.datetime.now().replace(microsecond=0)
    
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
    time_p = dt.datetime.now().replace(microsecond=0)
    
    # Ceck if lulc Rst has an valid format
    outIsRst = is_rst(lulcRst)
    if not outIsRst:
        from glass.pys.oss import fprop
        lulcRst = os.path.join(
            os.path.dirname(lulcRst),
            fprop(lulcRst, 'fn') + '.tif'
        )
    
    grs_to_rst(outGrs, lulcRst, as_cmd=True)
    osmlulc_rsttbl(nomenclature, os.path.join(
        os.path.dirname(lulcRst), os.path.basename(lulcRst) + '.vat.dbf'
    ))
    
    time_q = dt.datetime.now().replace(microsecond=0)

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

def osm_to_lulc(osm, nomenclature, ref, lulc, overwrite=None, savedb=None, tmpfld=None):
    """
    Convert OSM Data into Land Use/Land Cover Information

    (Version 1.5)
    """

    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import datetime as dt
    import os
    import copy
    # ************************************************************************ #
    # glass dependencies #
    # ************************************************************************ #
    from glass.cons.osmtolulc import PRIORITY
    from glass.dtt.ext        import fext_to_geof
    from glass.dtt.mge        import same_attr_to_shp, shps_to_shp
    from glass.sql.db           import create_pgdb, drop_db
    from glass.it.db             import osm_to_psql
    from glass.sql.bkup          import dump_db
    from glass.ete.osm2lulc.mod1 import grs_vector
    from glass.ete.osm2lulc.mod2 import roads_fmdb
    from glass.ete.osm2lulc.m3_4 import grs_vect_selbyarea
    from glass.ete.osm2lulc.mod5 import grs_vect_bbuffer
    from glass.ete.osm2lulc.mod6     import vector_assign_pntags_to_build
    from glass.ete.osm2lulc.utilsv15 import nomenclature_id, lulc_to_osmfeat, osm_project, get_legend
    from glass.prj                   import def_prj
    from glass.prop.prj import get_epsg
    from glass.prop.feat import feat_count
    from glass.pys.oss import mkdir, fprop
    from glass.pys.tm import now_as_str
    from glass.wenv.grs import run_grass
    # ************************************************************************ #
    # Global Settings #
    # ************************************************************************ #
    # Check if input parameters exists!
    if not os.path.exists(os.path.dirname(lulc)):
        raise ValueError(f'{os.path.dirname(lulc)} does not exist!')
    
    if not os.path.exists(osm):
        raise ValueError(f'File with OSM DATA ({osm}) does not exist!')
    
    if not os.path.exists(ref):
        raise ValueError(f'File with reference area ({ref}) does not exist!')
    
    # Check if Nomenclature is valid
    nom_id = nomenclature_id(nomenclature)

    if not nom_id:
        raise ValueError(f'Nomenclature {nomenclature} does not exist!')
    
    lulc_priority = PRIORITY[nomenclature]
    leg_df = get_legend(nom_id, fid_col='fid', leg_col='leg')
    legend = {r.fid: r.leg for i, r in leg_df.iterrows()}
    
    time_a = dt.datetime.now().replace(microsecond=0)

    # Create workspace for temporary files
    ws = os.path.join(os.path.dirname(lulc), now_as_str()) \
        if not tmpfld else tmpfld
    
    # Check if workspace exists
    if os.path.exists(ws):
        if overwrite:
            mkdir(ws)
        else:
            raise ValueError(f'Path {ws} already exists')
    else:
        mkdir(ws)
    
    # Get EPSG
    epsg, isproj = get_epsg(ref, is_proj=True)
    
    # Get Reference Raster
    refrst = fext_to_geof(
        ref, os.path.join(ws, 'refraster.tif'),
        ocellsize=10,
        epsg=epsg, oepsg=None if isproj else 3857
    )

    if not isproj:
        epsg = 3857

    time_b = dt.datetime.now().replace(microsecond=0)

    # ******************************************************************** #
    # Convert OSM file to PSQL DB #
    # ******************************************************************** #
    osm_db = create_pgdb(fprop(osm, 'fn', forceLower=True), overwrite=True)
    osm_db = osm_to_psql(osm, osm_db)

    time_c = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # Add Lulc Classes to OSM_FEATURES by rule #
    # ************************************************************************ #
    lulc_to_osmfeat(osm_db, nom_id)
    time_d = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # Transform SRS of OSM Data #
    # ************************************************************************ #
    osm_tbl = osm_project(
        osm_db, epsg,
        isGlobeLand=None if nomenclature != 'glob' else True
    )
    time_e = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Start a GRASS GIS Session #
    # ************************************************************************ #
    loc = 'osmtolulc'
    gb = run_grass(ws, location=loc, srs=refrst)

    import grass.script.setup as gsetup
    gsetup.init(gb, ws, loc, 'PERMANENT')

    time_f = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # IMPORT SOME glass MODULES FOR GRASS GIS #
    # ************************************************************************ #
    from glass.gp.ovl   import erase
    from glass.it.shp   import shp_to_grs, grs_to_shp
    from glass.tbl.grs  import del_table, add_table, reset_table, cols_calc
    from glass.gp.gen   import dissolve
    from glass.tbl.col  import add_fields
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    osm_shps = []
    # ************************************************************************ #
    # 1 - Selection Rule #
    # ************************************************************************ #
    mod1shp, time_check1 = grs_vector(osm_db, osm_tbl['polygons'])
    osm_shps.append(mod1shp)

    time_g = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 2 - Get Information About Roads Location #
    # ************************************************************************ #
    mod2shp, time_check2 = roads_fmdb(
        osm_db, osm_tbl['lines'], osm_tbl['polygons']
    )
    osm_shps.append(mod2shp)

    time_h = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # 3 - Area Upper than #
    # ************************************************************************ #
    if nom_id != 3:
        mod3shp, time_check3 = grs_vect_selbyarea(
            osm_db, osm_tbl['polygons'], UPPER=True
        )
        osm_shps.append(mod3shp)
        time_l = dt.datetime.now().replace(microsecond=0)
    
    else:
        time_check3, time_l = None, None
    
    # ************************************************************************ #
    # 4 - Area Lower than #
    # ************************************************************************ #
    if nom_id != 3:
        mod4shp, time_check4 = grs_vect_selbyarea(
            osm_db, osm_tbl['polygons'], UPPER=False
        )
        osm_shps.append(mod4shp)
        time_j = dt.datetime.now().replace(microsecond=0)
    
    else:
        time_check4, time_j = None, None
    
    # ************************************************************************ #
    # 5 - Get data from lines table (railway | waterway) #
    # ************************************************************************ #
    mod5shp, time_check5 = grs_vect_bbuffer(osm_db, osm_tbl['lines'])

    osm_shps.append(mod5shp)

    time_m = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # 6 - Assign untagged Buildings to tags #
    # ************************************************************************ #
    if nom_id != 3:
        urban, srv, time_check6 = vector_assign_pntags_to_build(
            osm_db, osm_tbl['points'], osm_tbl['polygons']
        )

        if urban:
            osm_shps.append(urban)
        
        if srv:
            osm_shps.append(srv)
    
    else:
        time_check6 = None
    
    time_n = dt.datetime.now().replace(microsecond=0)

    # ************************************************************************ #
    # Produce LULC Map  #
    # ************************************************************************ #
    """
    Get Shps with all geometries related with one class - One Shape for Classe
    """

    oshps = []
    for i in range(len(osm_shps)):
        if not osm_shps[i]: continue

        modshp = grs_to_shp(
            osm_shps[i], os.path.join(ws, f'{osm_shps[i]}.shp'),
            'auto', lyrn=1, ascmd=True, asMultiPart=None
        )

        nfeat = feat_count(modshp)

        if not nfeat: continue

        oshps.append(modshp)
    
    for shp in oshps:
        def_prj(f'{os.path.splitext(shp)[0]}.prj', epsg=epsg, api='epsgio')
    
    oshps = same_attr_to_shp(
        oshps, "cat", ws,
        basename="osm_", res_as_dict=True
    )

    time_o = dt.datetime.now().replace(microsecond=0)

    """
    Merge all Classes into one feature class using a priority rule
    """
    gshps = {int(c) : shp_to_grs(
        oshps[c], f"osm_{c}", asCMD=True
    ) for c in oshps}

    # Erase overlapping areas by priority
    osm_refname = copy.deepcopy(gshps)

    for e in range(len(lulc_priority)):
        if e + 1 == len(lulc_priority): break

        if lulc_priority[e] not in gshps: continue

        for i in range(e+1, len(lulc_priority)):
            if lulc_priority[i] not in gshps: continue

            gshps[lulc_priority[i]] = erase(
                gshps[lulc_priority[i]],
                gshps[lulc_priority[e]],
                f"{osm_refname[lulc_priority[i]]}_{e}",
                notTbl=False, api='pygrass'
            )

            nfeat = feat_count(
                gshps[lulc_priority[i]], gisApi='grass',
                work=ws, loc=loc
            )

            if not nfeat:
                del gshps[lulc_priority[i]]
                continue

            del_table(gshps[lulc_priority[i]])
            add_table(gshps[lulc_priority[i]], None)
    
    time_p = dt.datetime.now().replace(microsecond=0)

    # Export all classes
    lst_merge = []
    for i in range(len(lulc_priority)):
        if lulc_priority[i] not in gshps: continue

        reset_table(
            gshps[lulc_priority[i]],
            {'cls' : 'varchar(5)', 'leg' : 'varchar(75)'},
            {'cls' : str(lulc_priority[i]), 'leg' : str(legend[lulc_priority[i]])}
        )

        ds = dissolve(
            gshps[lulc_priority[i]],
            f'dl_{str(lulc_priority[i])}', 'cls', api="grass"
        )

        add_fields(ds, {'leg': 'varchar(75)'}, api="grass")
        cols_calc(ds, 'leg', str(legend[lulc_priority[i]]), 'leg is null')

        lst_merge.append(grs_to_shp(
            ds, os.path.join(
                ws, f"lulc_{str(lulc_priority[i])}.shp"
            ), 'auto', lyrn=1, ascmd=True, asMultiPart=None
        ))
    
    time_q = dt.datetime.now().replace(microsecond=0)

    if fprop(lulc, 'ff') != '.shp':
        lulc = os.path.join(os.path.dirname(lulc), fprop(lulc, 'fn') + '.shp')
    
    shps_to_shp(lst_merge, lulc, api='pandas')

    # Check if prj of lulcShp exists and create it if necessary
    prj_ff = os.path.splitext(lulc)[0] + '.prj'
    if not os.path.exists(prj_ff):
        def_prj(prj_ff, epsg=epsg, api='epsgio')
    
    time_r = dt.datetime.now().replace(microsecond=0)

    # Dump Database if PostGIS was used
    if savedb:
        dump_db(osm_db, savedb, api='psql')
    
    # Drop Database if PostGIS was used
    drop_db(osm_db)

    return lulc, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('set_grass', time_f - time_e),
        5  : ('rule_1', time_g - time_f, time_check1),
        6  : ('rule_2', time_h - time_g, time_check2),
        7  : None if not time_check3 else ('rule_3', time_l - time_h, time_check3),
        8  : None if not time_check4 else ('rule_4', time_j - time_l, time_check4),
        9  : ('rule_5',
            time_m - time_j if time_check4 else time_m - time_h, time_check5),
        10 : None if not time_check6 else ('rule_7', time_n - time_m, time_check6),
        11 : ('disj_cls', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('export_cls', time_q - time_p),
        14 : ('merge_cls', time_r - time_q)
    }

