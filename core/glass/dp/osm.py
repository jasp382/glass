"""
Methods to extract OSM data from the internet
"""


def download_by_boundary(input_boundary, folder_out, osm_name, epsg,
                         GetUrl=True, db_name=None, geomCol=None,
                         justOneFeature=None):
    """
    Download data from OSM using a bounding box
    """
    
    import os
    from osgeo         import ogr
    from glass.pys.web import get_file
    from glass.pys.oss import os_name
    
    OS_NAME = os_name()
    
    EXTENTS = []
    
    if db_name and geomCol:
        """
        Assuming input_boundary is a PostgreSQL Table
        """
        
        from glass.pys          import obj_to_lst
        from glass.geo.gql.prop import tbl_ext
        
        for t in obj_to_lst(input_boundary):
            EXTENTS.append(tbl_ext(db_name, t, geomCol))
    
    else:
        if type(input_boundary) == dict:
            if 'top' in input_boundary and 'bottom' in input_boundary \
                and 'left' in input_boundary and 'right' in input_boundary:
                
                EXTENTS.append([
                    input_boundary['left'],input_boundary['right'],
                    input_boundary['bottom'], input_boundary['top']
                ])
        
            else:
                raise ValueError((
                    'input_boundary is a dict but the keys are not correct. '
                    'Please use left, right, top and bottom as keys'
                ))
    
        elif type(input_boundary) == list:
            if len(input_boundary) == 4:
                EXTENTS.append(input_boundary)
        
            else:
                raise ValueError((
                    'input boundary is a list with more than 4 objects. '
                    'The list should be like: '
                    'l = [left, right, bottom, top]'
                ))
    
        elif type(input_boundary) == ogr.Geometry:
            EXTENTS.append(input_boundary.GetEnvelope())
    
        else:
            # Assuming input boundary is a file
        
            #Check if file exists
            if not os.path.exists(input_boundary):
                raise ValueError((
                    "Sorry, but the file {} does not exist inside the folder {}!"
                ).format(
                    os.path.basename(input_boundary),
                    os.path.dirname(input_boundary)
                ))
        
            # Check if is a raster
            from glass.geo.prop.df import check_isRaster
            isRst = check_isRaster(input_boundary)
        
            # Get EPSG
            if not epsg:
                from glass.geo.prop.prj import get_epsg
            
                epsg = get_epsg(input_boundary)
        
            if isRst:
                from glass.geo.prop.rst import rst_ext
            
                # Get raster extent
                EXTENTS.append(rst_ext(input_boundary))
        
            else:
                from glass.geo.prop.df import drv_name
                
                # Todo: check if it is shape
                
                # Open Dataset
                inSrc = ogr.GetDriverByName(drv_name(
                    input_boundary)).Open(input_boundary)
                
                lyr = inSrc.GetLayer()
                
                i = 1
                for feat in lyr:
                    geom = feat.GetGeometryRef()
                    
                    featext = geom.GetEnvelope()
                    
                    EXTENTS.append(featext)
                    
                    if justOneFeature:
                        break
    
    if epsg != 4326:
        from glass.geo.obj.g   import new_pnt
        from glass.geo.obj.prj import prj_ogrgeom
        
        for i in range(len(EXTENTS)):
            bottom_left = prj_ogrgeom(new_pnt(
                EXTENTS[i][0], EXTENTS[i][2]), epsg, 4326)
        
            top_right   = prj_ogrgeom(new_pnt(
                EXTENTS[i][1], EXTENTS[i][3]), epsg, 4326)
        
            left , bottom = bottom_left.GetX(), bottom_left.GetY()
            right, top    = top_right.GetX()  , top_right.GetY()
            
            EXTENTS[i] = [left, right, bottom, top]
    
    #url = "https://overpass-api.de/api/map?bbox={}"
    url = "https://lz4.overpass-api.de/api/interpreter?bbox={}"
    
    RESULTS = []
    for e in range(len(EXTENTS)):
        bbox_str = ','.join([str(p) for p in EXTENTS[e]])
        
        if GetUrl:
            RESULTS.append(url.format(bbox_str))
            continue
        
        if len(EXTENTS) == 1:
            outOsm = os.path.join(folder_out, osm_name + '.xml')
        else:
            outOsm = os.path.join(folder_out, "{}_{}.xml".format(osm_name, str(e)))
        
        osm_file = get_file(
            url.format(bbox_str), outOsm,
            useWget=None if OS_NAME == 'Windows' else None
        )
        
        RESULTS.append(osm_file)
    
    return RESULTS[0] if len(RESULTS) == 1 else RESULTS


def osm_from_geofabrik(out_folder):
    """
    Get all OSM Files in GeoFabrik
    """
    
    import os
    from glass.pys.web  import get_file
    from glass.cons.osm import osm_files
    from glass.pys.oss  import mkdir

    main_url = "http://download.geofabrik.de/{}/{}-latest.osm.pbf"

    for c in osm_files:
        if c == 'russia':
            get_file(
                "http://download.geofabrik.de/russia-latest.osm.pbf",
                os.path.join(out_folder, "russia-latest.osm.pbf")
            )
            continue
        
        # Create folder for that continent
        cf = mkdir(os.path.join(out_folder, c))

        # Download files of every continent
        for _c in osm_files[c]:
            get_file(main_url.format(c, _c), os.path.join(
                cf, 
                "{}-latest.osm.pbf".format(_c.replace('/', '_'))
            ), useWget=True)

    return out_folder


"""
OSM to DB
"""

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
    
    from glass.pys     import obj_to_lst
    from glass.pys.oss import fprop
    from glass.sql.prop   import cols_name
    from glass.sql.q   import q_to_ntbl
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
        from glass.dct.sql.fm import dump_tbls
        
        return dump_tbls(db, osmgeotbl + [osmcatbl] + osmreltbl, outSQL)
