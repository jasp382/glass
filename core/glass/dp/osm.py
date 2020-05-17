"""
OSM to DB
"""

def osm_to_relationaldb(osmData, inSchema, osmGeoTbl, osmCatTbl, osmRelTbl,
                        outSQL=None, db_name=None):
    """
    PostgreSQL - OSM Data to Relational Model
    
    E.g.
    osmData = '/mnt/d/mystuff/flainar/portugal-latest.osm.pbf'
    inSchema = {
        "TBL" : ['points', 'lines', 'multipolygons'],
        'FID' : 'ogc_fid',
        "COLS" : [
            'name', 'osm_id',
            #"ST_X(wkb_geometry) AS longitude",
            #"ST_Y(wkb_geometry) AS latitude",
            "wkb_geometry AS geom",
            "NULL AS featurecategoryid",
            "NULL AS flainarcategoryid",
            "NULL AS createdby",
            "NOW() AS createdon",
            "NULL AS updatedon",
            "NULL AS deletedon"
        ],
        "NOT_KEYS" : [
            'ogc_fid', 'osm_id', 'name', "wkb_geometry",
            'healthcare2', 'other_tags', 'osm_way_id',
            'ref', 'sidewalk', 'z_order', 'is_in', 'cuisine',
            'barrier', 'busway'
        ]
    }

    osmGeoTbl = {
        "points" : {"TBL" : 'osm_position', "FID" : 'positionid'},
        "multipolygons" : {"TBL" : "osm_polygons", "FID" : 'polygonid'},
        "lines" : {"TBL" : 'osm_lines', "FID" : 'lineid'}
    }

    osmCatTbl = {
        "TBL" : 'osmcategory', "FID" : "osmcategoryid",
        "KEY_COL" : "key", "VAL_COL" : "value",
        "COLS" : [
            "NULL AS createdby", "NOW() AS createdon",
            "NULL AS updatedon", "NULL AS deletedon"
        ]
    }

    osmRelTbl = {
        "points" : {"TBL" : "position_osmcat", "FID" : 'pososmcatid'},
        "multipolygons" : {"TBL" : "polygons_osmcat", "FID" : 'polygoncatid'},
        "lines" : {"TBL" : "lines_osmcat", "FID" : 'linecatid'},
    }

    outSQL = '/mnt/d/mystuff/flainar/portugal-osmdb.sql'

    db_name='osm_pt'
    """
    
    from glass.pys         import obj_to_lst
    from glass.pys.oss     import fprop
    from glass.prop.sql import cols_name
    from glass.sql.q    import q_to_ntbl
    from glass.sql.db   import create_db
    from glass.it.db     import osm_to_psql

    inSchema["TBL"] = obj_to_lst(inSchema["TBL"])
    
    # Create DB
    osm_fn = fprop(osmData, 'fn')
    osm_fn = osm_fn.replace('-', '').replace('.', '')
    db = create_db(osm_fn if not db_name else db_name, api='psql')
    
    # Send OSM data to Database
    osm_to_psql(osmData, db)
    
    # Get KEYS COLUMNS
    transcols = {}
    for tbl in inSchema["TBL"]:
        transcols[tbl] = [c for c in cols_name(
            db, tbl, sanitizeSpecialWords=None
        ) if c not in inSchema["NOT_KEYS"]]
    
    # Create osmGeoTbl
    osmgeotbl = [q_to_ntbl(db, osmGeoTbl[tbl]['TBL'], (
        "SELECT {} AS {}, {} FROM {}"
    ).format(
        inSchema["FID"], osmGeoTbl[tbl]["FID"],
        ", ".join(inSchema["COLS"]), tbl
    ), api='psql') for tbl in inSchema["TBL"]]
    
    # Create OSM categories table
    qs = []
    for tbl in inSchema["TBL"]:
        qs.extend([(
            "SELECT '{keyV}' AS {keyC}, CAST({t}.{keyV} AS text) AS {valC} "
            "FROM {t} WHERE {t}.{keyV} IS NOT NULL "
            "GROUP BY {t}.{keyV}"
        ).format(
            keyV=c, t=tbl, keyC=osmCatTbl["KEY_COL"],
            valC=osmCatTbl["VAL_COL"]
        ) for c in transcols[tbl]])
    
    osmcatbl = q_to_ntbl(db, osmCatTbl["TBL"], (
        "SELECT row_number() OVER(ORDER BY {keyC}) "
        "AS {osmcatid}, {keyC}, {valC}{ocols} "
        "FROM ({q}) AS foo"
    ).format(
        q="SELECT {k}, {v} FROM ({t}) AS kvtbl GROUP BY {k}, {v}".format(
            k=osmCatTbl["KEY_COL"], v=osmCatTbl["VAL_COL"],
            t=" UNION ALL ".join(qs), 
        ) if len(inSchema["TBL"]) > 1 else " UNION ALL ".join(qs),
        keyC=osmCatTbl["KEY_COL"],
        osmcatid=osmCatTbl["FID"], valC=osmCatTbl["VAL_COL"],
        ocols="" if "COLS" not in osmCatTbl else ", {}".format(
            ", ".join(osmCatTbl["COLS"])
        )
    ), api='psql')
    
    # Create relation table
    osmreltbl = []
    for tbl in inSchema["TBL"]:
        qs = [(
            "SELECT {fid}, '{keyV}' AS key, CAST({t}.{keyV} AS text) AS osmval "
            "FROM {t} WHERE {t}.{keyV} IS NOT NULL"
        ).format(
            fid=inSchema["FID"], keyV=c, t=tbl
        ) for c in transcols[tbl]]
    
        osmreltbl.append(q_to_ntbl(db, osmRelTbl[tbl]["TBL"], (
            "SELECT foo.{fid} AS {nfid}, catbl.{osmcatfid} "
            "FROM ({mtbl}) AS foo INNER JOIN {catTbl} AS catbl "
            "ON foo.key = catbl.{catkey} AND foo.osmval = catbl.{catval}"
        ).format(
            mtbl=" UNION ALL ".join(qs), fid=inSchema["FID"],
            nfid=osmRelTbl[tbl]["FID"],
            catTbl=osmCatTbl["TBL"], osmcatfid=osmCatTbl["FID"],
            catkey=osmCatTbl["KEY_COL"], catval=osmCatTbl["VAL_COL"]
        ), api='psql'))
    
    if not outSQL:
        return osmgeotbl, osmcatbl, osmreltbl
    else:
        from glass.sql.bkup import dump_tbls
        
        return dump_tbls(db, osmgeotbl + [osmcatbl] + osmreltbl, outSQL)

