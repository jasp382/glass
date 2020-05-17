"""
Generic method to select all osm features to be used in a certain rule
"""

from glass.ete.osm2lulc import DB_SCHEMA, PROCEDURE_DB


def record_time_consumed(timeData, outXls):
    """
    Record the time consumed by a OSM2LULC procedure version
    in a excel table
    """
    
    import pandas
    from glass.wt import obj_to_tbl
    
    # Produce main table - Time consumed by rule
    main = [{
        'rule' : timeData[i][0], 'time' : timeData[i][1]
    } for i in range(len(timeData.keys())) if timeData[i]]
    
    # Produce detailed table - Time consumed inside rules
    timeInsideRule = []
    timeDataKeys = list(timeData.keys())
    timeDataKeys.sort()
    
    for i in timeDataKeys:
        if not timeData[i]:
            continue
        
        if len(timeData[i]) == 2:
            timeInsideRule.append({
                'rule' : timeData[i][0],
                'task' : timeData[i][0],
                'time' : timeData[i][1]
            })
        
        elif len(timeData[i]) == 3:
            taskKeys = list(timeData[i][2].keys())
            taskKeys.sort()
            for task in taskKeys:
                if not timeData[i][2][task]:
                    continue
                
                timeInsideRule.append({
                    'rule' : timeData[i][0],
                    'task' : timeData[i][2][task][0],
                    'time' : timeData[i][2][task][1]
                })
        
        else:
            print('timeData object with key {} is not valid'.format(i))
    
    # Export tables to excel
    dfs = [pandas.DataFrame(main), pandas.DataFrame(timeInsideRule)]
    
    return obj_to_tbl(dfs, outXls, sheetsName=['general', 'detailed'])


def osm_project(osmDb, srs_epsg, api='SQLITE', isGlobeLand=None):
    """
    Reproject OSMDATA to a specific Spatial Reference System
    """
    
    if api != 'POSTGIS':
        from glass.prj  import proj
    else:
        from glass.sql.q       import q_to_ntbl as proj
        from glass.prop.sql.idx import idx_for_geom
    from glass.ete.osm2lulc     import osmTableData, GEOM_AREA
    
    osmtables = {}
    
    GEOM_COL = "geometry" if api != "POSTGIS" else "wkb_geometry"
    
    for table in osmTableData:
        if table == "polygons":
            Q = (
                "SELECT building, selection, buildings, area_upper, t_area_upper, "
                "area_lower, t_area_lower, {geomColTrans} AS geometry, "
                "ST_Area(ST_Transform({geomCol}, {epsg})) AS {geom_area} "
                "FROM {t} WHERE selection IS NOT NULL OR "
                "buildings IS NOT NULL OR area_upper IS NOT NULL OR "
                "area_lower IS NOT NULL"
            ).format(
                "" if isGlobeLand else "buildings, ",
                geomColTrans=GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                geomCol=GEOM_COL, epsg=srs_epsg,
                t=osmTableData[table], geom_area=GEOM_AREA
            ) if not isGlobeLand else (
                "SELECT building, selection, {geomColTrans} AS geometry FROM "
                "{t} WHERE selection IS NOT NULL"
            ).format(
                geomColTrans=GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                    t=osmTableData[table]
            )
        
        elif table == 'lines':
            Q = (
                "SELECT{} roads, bf_roads, basic_buffer, bf_basic_buffer, "
                "{} AS geometry FROM {} "
                "WHERE roads IS NOT NULL OR basic_buffer IS NOT NULL"
            ).format(
                "" if api != 'POSTGIS' else " row_number() OVER(ORDER BY roads) AS gid,",
                GEOM_COL if api != 'POSTGIS' else \
                    f"ST_Transform({GEOM_COL}, {srs_epsg})",
                osmTableData[table]
            )
        
        elif table == 'points':
            Q = "SELECT {}, {} AS geometry FROM {}{}".format(
                "NULL AS buildings" if isGlobeLand else "buildings",
                GEOM_COL if api != 'POSTGIS' else \
                    "ST_Transform({}, {})".format(GEOM_COL, srs_epsg),
                osmTableData[table],
                "" if isGlobeLand else " WHERE buildings IS NOT NULL"
            )
        
        nt = f'{table}_{str(srs_epsg)}'
        if api != 'POSTGIS':
            proj({'DB' : osmDb, 'TABLE' : table},
                nt, srs_epsg, inEPSG=4326,
                api='ogr2ogr_SQLITE', sql=Q
            )
        else:
            proj(osmDb, nt, Q, api='psql')
            
            idx_for_geom(osmDb, nt, "geometry")
        
        osmtables[table] = nt
    
    return osmtables


def get_osm_feat_by_rule(nomenclature):
    """
    Return OSM Features By rule
    """
    
    from glass.sql.q import q_to_obj
    
    Q = (
        "SELECT jtbl.{rellulccls} AS {rellulccls}, "
        "{osmfeat}.{key} AS {key}, {osmfeat}.{val} AS {val}, "
        "jtbl.{ruleName} AS {ruleName}, jtbl.{bufferCol} "
        "AS {bufferCol}, jtbl.{areaCol} AS {areaCol} "
        "FROM {osmfeat} INNER JOIN ("
            "SELECT {osmrel}.{relosmid}, {osmrel}.{rellulccls}, "
            "{rules}.{ruleID}, {rules}.{ruleName}, "
            "{osmrel}.{bufferCol}, {osmrel}.{areaCol} "
            "FROM {osmrel} "
            "INNER JOIN {rules} ON {osmrel}.{_ruleID} = {rules}.{ruleID} "
        ") AS jtbl ON {osmfeat}.{osmid} = jtbl.{relosmid}"
    ).format(
        osmfeat    = DB_SCHEMA["OSM_FEATURES"]["NAME"],
        osmid      = DB_SCHEMA["OSM_FEATURES"]["OSM_ID"],
        key        = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"],
        val        = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"],
        osmrel     = DB_SCHEMA[nomenclature]["OSM_RELATION"],
        relosmid   = DB_SCHEMA[nomenclature]["OSM_FK"],
        rellulccls = DB_SCHEMA[nomenclature]["CLS_FK"],
        _ruleID    = DB_SCHEMA[nomenclature]["RULE_FK"],
        rules      = DB_SCHEMA["RULES"]["NAME"],
        ruleID     = DB_SCHEMA["RULES"]["RULE_ID"],
        ruleName   = DB_SCHEMA["RULES"]["RULE_NAME"],
        bufferCol  = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"],
        areaCol    = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
    )
    
    return q_to_obj(PROCEDURE_DB, Q, db_api='sqlite')


def add_lulc_to_osmfeat(osmdb, osmTbl, nomenclature, api='SQLITE'):
    """
    Add LULC Classes in OSM Data Tables
    """
    
    from glass.sql.q        import exec_write_q
    from glass.ete.osm2lulc import DB_SCHEMA
    
    KEY_COL   = DB_SCHEMA["OSM_FEATURES"]["OSM_KEY"]
    VALUE_COL = DB_SCHEMA["OSM_FEATURES"]["OSM_VALUE"]
    LULC_COL  = DB_SCHEMA[nomenclature]["CLS_FK"]
    RULE_NAME = DB_SCHEMA["RULES"]["RULE_NAME"]
    
    osmFeaturesDf = get_osm_feat_by_rule(nomenclature)
    
    osmFeaturesDf.loc[:, VALUE_COL] = osmFeaturesDf[KEY_COL] + "='" + \
        osmFeaturesDf[VALUE_COL] + "'"
    
    Q = []
    for rule in osmFeaturesDf[RULE_NAME].unique():
        filterDf = osmFeaturesDf[osmFeaturesDf[RULE_NAME] == rule]
        
        if rule == 'selection' or rule == 'buildings':
            OSM_TABLE  = 'polygons'
            BUFFER_COL = None
            AREA_COL   = None
        
        elif rule == 'roads':
            OSM_TABLE  = 'lines'
            BUFFER_COL = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
            AREA_COL   = None
        
        elif rule == 'area_upper' or rule == 'area_lower':
            OSM_TABLE  = 'polygons'
            BUFFER_COL = None
            AREA_COL   = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["AREA"]
        
        elif rule == 'basic_buffer':
            OSM_TABLE  = 'lines'
            BUFFER_COL = DB_SCHEMA[nomenclature]["RULES_FIELDS"]["BUFFER"]
            AREA_COL   = None
        
        filterDf.loc[:, VALUE_COL] = osmTbl[OSM_TABLE] + "." + filterDf[VALUE_COL]
        
        Q.append(
            "ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], rule
            )
        )
        
        if BUFFER_COL:
            Q.append("ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], "bf_" + rule
            ))
        
        if AREA_COL:
            Q.append("ALTER TABLE {} ADD COLUMN {} integer".format(
                osmTbl[OSM_TABLE], "t_" + rule
            ))
        
        for cls in filterDf[LULC_COL].unique():
            __filterDf = filterDf[filterDf[LULC_COL] == cls]
        
            Q.append("UPDATE {} SET {}={} WHERE {}".format(
                osmTbl[OSM_TABLE], rule, cls,
                str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
            ))
        
        if BUFFER_COL:
            for bfdist in filterDf[BUFFER_COL].unique():
                __filterDf = filterDf[filterDf[BUFFER_COL] == bfdist]
                
                Q.append("UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl[OSM_TABLE], "bf_" + rule,
                    bfdist, str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
                ))
        
        if AREA_COL:
            for areaval in filterDf[AREA_COL].unique():
                __filterDf = filterDf[filterDf[AREA_COL] == areaval]
                
                Q.append("UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl[OSM_TABLE], "t_" + rule, areaval,
                    str(__filterDf[VALUE_COL].str.cat(sep=" OR "))
                ))
        
        if rule == 'buildings':
            fd = osmFeaturesDf[
                (osmFeaturesDf[RULE_NAME] == 'selection') & \
                (osmFeaturesDf[KEY_COL] == 'building') & \
                (osmFeaturesDf[LULC_COL] == 12)
            ]
            
            Q += [
                "ALTER TABLE {} ADD COLUMN {} integer".format(
                    osmTbl["points"], rule
                ),
                "UPDATE {} SET {}={} WHERE {}".format(
                    osmTbl["points"], rule, 12,
                    str(fd[VALUE_COL].str.cat(sep=" OR "))
                )
            ]
    
    exec_write_q(osmdb, Q, api='psql' if api == 'POSTGIS' else 'sqlite')


def osmlulc_rsttbl(nomenclature, outpath):
    
    import pandas;          import dbf
    from glass.ete.osm2lulc import LEGEND
    
    __legend = LEGEND[nomenclature]
    
    df = pandas.DataFrame([
        [k, __legend[k]] for k in __legend],
        columns=['Value', 'leg']
    )
    
    df = df.values.tolist()
    
    table = dbf.Table(outpath, 'Value N(4,0); leg C(75)')
    table.open(mode=dbf.READ_WRITE)
    
    for row in df:
        table.append(tuple(row))
    
    table.close()
    
    return outpath

