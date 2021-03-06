"""
Tools see which OSM tags are not being used in OSM2LULC
"""

def get_not_used_tags(OSM_FILE, OUT_TBL):
    """
    Use a file OSM to detect tags not considered in the
    OSM2LULC procedure
    """
    
    import os
    from glass.dct           import obj_to_tbl
    from glass.geo.df.filter      import sel_by_attr
    from glass.dct.sql.fm       import q_to_obj
    from glass.dp.pd.split     import df_split
    from glass.pys.oss          import fprop
    from glass.dct.geo.toshp.osm import osm_to_gpkg
    
    OSM_TAG_MAP = {
        "DB"        : os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'osmtolulc.sqlite'
        ),
        "OSM_FEAT"  : "osm_features",
        "KEY_COL"   : "key",
        "VALUE_COL" : "value",
        "GEOM_COL"  : "geom"
    }
    
    WORKSPACE = os.path.dirname(OUT_TBL)
    
    sqdb = osm_to_gpkg(OSM_FILE, os.path.join(
        WORKSPACE, fprop(OSM_FILE, 'fn') + '.gpkg'
    ))
    
    # Get Features we are considering
    ourOSMFeatures = q_to_obj(OSM_TAG_MAP["DB"], (
        "SELECT {key} AS key_y, {value} AS value_y, {geom} AS geom_y "
        "FROM {tbl}"
    ).format(
        key=OSM_TAG_MAP["KEY_COL"], value=OSM_TAG_MAP["VALUE_COL"],
        geom=OSM_TAG_MAP["GEOM_COL"], tbl=OSM_TAG_MAP["OSM_FEAT"]
    ), db_api='sqlite')
    
    # Get Features in File
    TABLES_TAGS = {
        'points'        : ['highway', 'man_made', 'building'],
        'lines'         : ['highway', 'waterway', 'aerialway', 'barrier',
                           'man_made', 'railway'],
        'multipolygons' : ['aeroway', 'amenity', 'barrier', 'building',
                           'craft', 'historic', 'land_area', ''
                           'landuse', 'leisure', 'man_made', 'military',
                           'natural', 'office', 'place', 'shop',
                           'sport', 'tourism', 'waterway', 'power',
                           'railway', 'healthcare', 'highway']
    }
    
    Qs = [
        " UNION ALL ".join([(
            "SELECT '{keycol}' AS key, {keycol} AS value, "
            "'{geomtype}' AS geom FROM {tbl} WHERE "
            "{keycol} IS NOT NULL"
        ).format(
            keycol=c, geomtype='Point' if table == 'points' else 'Line' \
                if table == 'lines' else 'Polygon',
            tbl=table
        ) for c in TABLES_TAGS[table]]) for table in TABLES_TAGS
    ]
    
    fileOSMFeatures = q_to_obj(sqdb, (
        "SELECT key, value, geom FROM ({}) AS foo "
        "GROUP BY key, value, geom"
    ).format(" UNION ALL ".join(Qs)), db_api='sqlite')
    
    _fileOSMFeatures = fileOSMFeatures.merge(
        ourOSMFeatures, how='outer',
        left_on=["key", "value", "geom"],
        right_on=["key_y", "value_y", "geom_y"]
    )
    
    # Select OSM Features of file without correspondence
    _fileOSMFeatures["isnew"] =_fileOSMFeatures.key_y.fillna(value='nenhum')
    
    newTags = _fileOSMFeatures[_fileOSMFeatures.isnew == 'nenhum']
    
    newTags["value"] = newTags.value.str.replace("'", "''")
    
    newTags["whr"] = newTags.key + "='" + newTags.value + "'"
    
    # Export tags not being used to new shapefile
    def to_regular_str(row):
        san_str = row.whr
        
        row["whr_san"] = san_str
        
        return row
    
    for t in TABLES_TAGS:
        if t == 'points':
            filterDf = newTags[newTags.geom == 'Point']
        
        elif t == 'lines':
            filterDf = newTags[newTags.geom == 'Line']
        
        elif t == 'multipolygons':
            filterDf = newTags[newTags.geom == 'Polygon']
        
        if filterDf.shape[0] > 500:
            dfs = df_split(filterDf, 500, nrows=True)
        else:
            dfs = [filterDf]
        
        Q = "SELECT * FROM {} WHERE {}".format(
            t, filterDf.whr.str.cat(sep=" OR "))
        
        i = 1
        for df in dfs:
            fn = t + '.shp' if len(dfs) == 1 else '{}_{}.shp'.format(
                t, str(i)
            )
            try:
                shp = sel_by_attr(sqdb, Q.format(
                    t, df.whr.str.cat(sep=" OR ")
                ), os.path.join(WORKSPACE, fn), api_gis='ogr')
            except:
                __df = df.apply(lambda x: to_regular_str(x), axis=1)
            
                shp = sel_by_attr(sqdb, Q.format(
                    t, __df.whr.str.cat(sep=" OR ")
                ), os.path.join(WORKSPACE, fn))
            
            i += 1
    
    # Export OUT_TBL with tags not being used
    newTags.drop(['key_y', 'value_y', 'geom_y', 'isnew', 'whr'], axis=1, inplace=True)
    obj_to_tbl(newTags, OUT_TBL, sheetsName="new_tags", sanitizeUtf8=True)
    
    return OUT_TBL

