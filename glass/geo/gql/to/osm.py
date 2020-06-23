"""
OSM to DB
"""

def osm_to_psql(osmXml, osmdb):
    """
    Use GDAL to import osmfile into PostGIS database
    """
    
    from glass.pyt       import execmd
    from glass.cons.psql import con_psql
    from glass.sql.i     import db_exists

    is_db = db_exists(osmdb)

    if not is_db:
        from glass.sql.db import create_db

        create_db(osmdb, api='psql')

    con = con_psql()
    
    cmd = (
        "ogr2ogr -f PostgreSQL \"PG:dbname='{}' host='{}' port='{}' "
        "user='{}' password='{}'\" {} -lco COLUM_TYPES=other_tags=hstore"
    ).format(
        osmdb, con["HOST"], con["PORT"],
        con["USER"], con["PASSWORD"], osmXml
    )
    
    cmdout = execmd(cmd)
    
    return osmdb


def osm_to_relationaldb(osmData, inSchema, osmGeoTbl, osmCatTbl, osmRelTbl,
                        outSQL=None, db_name=None):
    """
    PostgreSQL - OSM Data to Relational Model
    
    TODO: Just work for one geom table at once
    
    E.g.
    osmData = '/home/jasp/flainar/osm_centro.xml'
    
    inSchema = {
        "TBL" : ['points', 'lines', 'multipolygons'],
        'FID' : 'CAST(osm_id AS bigint)',
        "COLS" : [
            'name',
            "ST_X(wkb_geometry) AS longitude",
            "ST_Y(wkb_geometry) AS latitude",
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
            'healthcare2', 'other_tags'
        ]
    }
    
    osmGeoTbl = {"TBL" : 'position', "FID" : 'positionid'}
    
    osmCatTbl = {
        "TBL" : 'osmcategory', "FID" : "osmcategoryid",
        "KEY_COL" : "keycategory", "VAL_COL" : "value",
        "COLS" : [
            "NULL AS createdby", "NOW() AS createdon",
            "NULL AS updatedon", "NULL AS deletedon"
        ]
    }
    
    osmRelTbl = {
        "TBL" : "position_osmcat", "FID" : 'pososmcatid'
    }
    """
    
    from glass.pyt     import obj_to_lst
    from glass.pyt.oss import fprop
    from glass.sql.i   import cols_name
    from glass.sql.to  import q_to_ntbl
    from glass.sql.db  import create_db

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
        from glass.sql.fm import dump_tbls
        
        return dump_tbls(db, osmgeotbl + [osmcatbl] + osmreltbl, outSQL)
