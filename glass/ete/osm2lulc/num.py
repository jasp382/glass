"""
OSM2LULC using Numpy
"""

def rstcls_map(rstcode):
    if rstcode == 98:
        return 1222
    elif rstcode == 99:
        return 1221
    elif rstcode == 82:
        return 802
    elif rstcode == 142:
        return 97
    elif rstcode == 1421:
        return 96
    elif rstcode == 141:
        return 95
    elif rstcode == 321:
        return 94
    elif rstcode == 324:
        return 93
    elif rstcode == 81:
        return 801
    else:
        return rstcode

def osm2lulc(osmdata, nomenclature, refRaster, lulcRst,
             overwrite=None, dataStore=None, roadsAPI='POSTGIS'):
    """
    Convert OSM data into Land Use/Land Cover Information
    
    A matrix based approach
    
    roadsAPI Options:
    * SQLITE
    * POSTGIS
    """
    
    # ************************************************************************ #
    # Python Modules from Reference Packages #
    # ************************************************************************ #
    import os
    import numpy as np
    import datetime as dt
    from threading import Thread
    # ************************************************************************ #
    # Dependencies #
    # ************************************************************************ #
    from glass.rd.rst                import rst_to_array
    from glass.prop                  import is_rst
    from glass.prop.rst              import get_cellsize
    from glass.pys.oss               import mkdir, copy_file
    from glass.pys.oss               import fprop
    if roadsAPI == 'POSTGIS':
        from glass.sql.db            import create_db
        from glass.it.db             import osm_to_psql
        from glass.ete.osm2lulc.mod2 import pg_num_roads
        from glass.sql.bkup          import dump_db
        from glass.sql.db            import drop_db
    else:
        from glass.it.osm            import osm_to_sqdb
        from glass.ete.osm2lulc.mod2 import num_roads
    from glass.ete.osm2lulc          import NOMENCLATURES
    from glass.ete.osm2lulc.utils    import osm_project, add_lulc_to_osmfeat
    from glass.ete.osm2lulc.utils    import osmlulc_rsttbl
    from glass.ete.osm2lulc.utils    import get_ref_raster
    from glass.ete.osm2lulc.mod1     import num_selection
    from glass.ete.osm2lulc.m3_4     import num_selbyarea
    from glass.ete.osm2lulc.mod5     import num_base_buffer
    from glass.ete.osm2lulc.mod6     import num_assign_builds
    from glass.wt.rst                import obj_to_rst
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
    nomenclature = "URBAN_ATLAS" if nomenclature not in NOMENCLATURES else \
        nomenclature
    
    time_a = dt.datetime.now().replace(microsecond=0)
    
    workspace = os.path.join(os.path.dirname(
        lulcRst), 'num_osmto') if not dataStore else dataStore
    
    # Check if workspace exists:
    if os.path.exists(workspace):
        if overwrite:
            mkdir(workspace, overwrite=True)
        else:
            raise ValueError(f'Path {workspace} already exists')
    else:
        mkdir(workspace, overwrite=None)
    
    # Get Ref Raster and EPSG
    refRaster, epsg = get_ref_raster(refRaster, workspace, cellsize=2)
    CELLSIZE = get_cellsize(refRaster, gisApi='gdal')
        
    from glass.ete.osm2lulc import osmTableData, PRIORITIES
    
    time_b = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # Convert OSM file to SQLITE DB or to POSTGIS DB #
    # ************************************************************************ #
    if roadsAPI == 'POSTGIS':
        osm_db = create_db(fprop(
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
        isGlobeLand=None if nomenclature != "GLOBE_LAND_30" else True
    )
    time_e = dt.datetime.now().replace(microsecond=0)
    # ************************************************************************ #
    # MapResults #
    # ************************************************************************ #
    mergeOut  = {}
    timeCheck = {}
    RULES = [1, 2, 3, 4, 5, 7]
    
    def run_rule(ruleID):
        time_start = dt.datetime.now().replace(microsecond=0)
        _osmdb = copy_file(
            osm_db, os.path.splitext(osm_db)[0] + '_r{}.sqlite'.format(ruleID)
        ) if roadsAPI == 'SQLITE' else None
        # ******************************************************************** #
        # 1 - Selection Rule #
        # ******************************************************************** #
        if ruleID == 1:
            res, tm = num_selection(
                _osmdb if _osmdb else osm_db, osmTableData['polygons'], workspace,
                CELLSIZE, epsg, refRaster, api=roadsAPI
            )
        # ******************************************************************** #
        # 2 - Get Information About Roads Location #
        # ******************************************************************** #
        elif ruleID == 2:
            res, tm = num_roads(
                _osmdb, nomenclature, osmTableData['lines'],
                osmTableData['polygons'], workspace, CELLSIZE, epsg,
                refRaster
            ) if _osmdb else pg_num_roads(
                osm_db, nomenclature,
                osmTableData['lines'], osmTableData['polygons'],
                workspace, CELLSIZE, epsg, refRaster
            )
        
        # ******************************************************************** #
        # 3 - Area Upper than #
        # ******************************************************************** #
        elif ruleID == 3:
            if nomenclature != "GLOBE_LAND_30":
                res, tm = num_selbyarea(
                    osm_db if not _osmdb else _osmdb,
                    osmTableData['polygons'], workspace,
                    CELLSIZE, epsg, refRaster, UPPER=True, api=roadsAPI
                )
            else:
                return
        
        # ******************************************************************** #
        # 4 - Area Lower than #
        # ******************************************************************** #
        elif ruleID == 4:
            if nomenclature != "GLOBE_LAND_30":
                res, tm = num_selbyarea(
                    osm_db if not _osmdb else _osmdb,
                    osmTableData['polygons'], workspace,
                    CELLSIZE, epsg, refRaster, UPPER=False, api=roadsAPI
                )
            else:
                return
        
        # ******************************************************************** #
        # 5 - Get data from lines table (railway | waterway) #
        # ******************************************************************** #
        elif ruleID == 5:
            res, tm = num_base_buffer(
                osm_db if not _osmdb else _osmdb,
                osmTableData['lines'], workspace,
                CELLSIZE, epsg, refRaster, api=roadsAPI
            )
        # ******************************************************************** #
        # 7 - Assign untagged Buildings to tags #
        # ******************************************************************** #
        elif ruleID == 7:
            if nomenclature != "GLOBE_LAND_30":
                res, tm = num_assign_builds(
                    osm_db if not _osmdb else _osmdb,
                    osmTableData['points'], osmTableData['polygons'],
                    workspace, CELLSIZE, epsg, refRaster, apidb=roadsAPI
                )
            
            else:
                return
        
        time_end = dt.datetime.now().replace(microsecond=0)
        mergeOut[ruleID] = res
        timeCheck[ruleID] = {'total': time_end - time_start, 'detailed': tm}
    
    thrds = []
    for r in RULES:
        thrds.append(Thread(
            name="to_{}".format(str(r)), target=run_rule,
            args=(r,)
        ))
        
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    # Merge all results into one Raster
    compileResults = {}
    for rule in mergeOut:
        for cls in mergeOut[rule]:
            if cls not in compileResults:
                if type(mergeOut[rule][cls]) == list:
                    compileResults[cls] = mergeOut[rule][cls]
                else:
                    compileResults[cls] = [mergeOut[rule][cls]]
            
            else:
                if type(mergeOut[rule][cls]) == list:
                    compileResults[cls] += mergeOut[rule][cls]
                else:
                    compileResults[cls].append(mergeOut[rule][cls])
    
    time_m = dt.datetime.now().replace(microsecond=0)
    # All Rasters to Array
    arrayRst = {}
    for cls in compileResults:
        for raster in compileResults[cls]:
            if not raster:
                continue
            
            array = rst_to_array(raster)
            
            if cls not in arrayRst:
                arrayRst[cls] = [array.astype(np.uint8)]
            
            else:
                arrayRst[cls].append(array.astype(np.uint8))
    time_n = dt.datetime.now().replace(microsecond=0)
    
    # Sum Rasters of each class
    for cls in arrayRst:
        if len(arrayRst[cls]) == 1:
            sumArray = arrayRst[cls][0]
        
        else:
            sumArray = arrayRst[cls][0]
            
            for i in range(1, len(arrayRst[cls])):
                sumArray = sumArray + arrayRst[cls][i]
        
        arrayRst[cls] = sumArray
    
    time_o = dt.datetime.now().replace(microsecond=0)
    
    # Apply priority rule
    __priorities = PRIORITIES[nomenclature + "_NUMPY"]
    
    for lulcCls in __priorities:
        __lulcCls = rstcls_map(lulcCls)

        if __lulcCls not in arrayRst:
            continue
        else:
            np.place(arrayRst[__lulcCls], arrayRst[__lulcCls] > 0,
                lulcCls
            )
    
    for i in range(len(__priorities)):
        lulc_i = rstcls_map(__priorities[i])

        if lulc_i not in arrayRst:
            continue
        
        else:
            for e in range(i+1, len(__priorities)):
                lulc_e = rstcls_map(__priorities[e])

                if lulc_e not in arrayRst:
                    continue
                
                else:
                    np.place(arrayRst[lulc_e],
                        arrayRst[lulc_i] == __priorities[i], 0
                    )
    
    time_p = dt.datetime.now().replace(microsecond=0)
    
    # Merge all rasters
    startCls = 'None'
    for i in range(len(__priorities)):
        lulc_i = rstcls_map(__priorities[i])
        
        if lulc_i in arrayRst:
            resultSum = arrayRst[lulc_i]
            startCls = i
            break
    
    if startCls == 'None':
        return 'NoResults'
    
    for i in range(startCls + 1, len(__priorities)):
        lulc_i = rstcls_map(__priorities[i])
        
        if lulc_i not in arrayRst:
            continue
        
        resultSum = resultSum + arrayRst[lulc_i]
    
    # Save Result
    outIsRst = is_rst(lulcRst)
    if not outIsRst:
        from glass.pys.oss import fprop
        
        lulcRst = os.path.join(
            os.path.dirname(lulcRst), fprop(lulcRst, 'fn') + '.tif'
        )
    
    np.place(resultSum, resultSum==0, 1)
    obj_to_rst(resultSum, lulcRst, refRaster, noData=1)
    
    osmlulc_rsttbl(nomenclature + "_NUMPY", os.path.join(
        os.path.dirname(lulcRst), os.path.basename(lulcRst) + '.vat.dbf'
    ))
    
    time_q = dt.datetime.now().replace(microsecond=0)

    # Dump Database if PostGIS was used
    # Drop Database if PostGIS was used
    if roadsAPI == 'POSTGIS':
        dump_db(osm_db, os.path.join(workspace, osm_db + '.sql'), api='psql')
        drop_db(osm_db)
    
    return lulcRst, {
        0  : ('set_settings', time_b - time_a),
        1  : ('osm_to_sqdb', time_c - time_b),
        2  : ('cls_in_sqdb', time_d - time_c),
        3  : ('proj_data', time_e - time_d),
        4  : ('rule_1', timeCheck[1]['total'], timeCheck[1]['detailed']),
        5  : ('rule_2', timeCheck[2]['total'], timeCheck[2]['detailed']),
        6  : None if 3 not in timeCheck else (
            'rule_3', timeCheck[3]['total'], timeCheck[3]['detailed']),
        7  : None if 4 not in timeCheck else (
            'rule_4', timeCheck[4]['total'], timeCheck[4]['detailed']),
        8  : ('rule_5', timeCheck[5]['total'], timeCheck[5]['detailed']),
        9  : None if 7 not in timeCheck else (
            'rule_7', timeCheck[7]['total'], timeCheck[7]['detailed']),
        10 : ('rst_to_array', time_n - time_m),
        11 : ('sum_cls', time_o - time_n),
        12 : ('priority_rule', time_p - time_o),
        13 : ('merge_rst', time_q - time_p)
    }
