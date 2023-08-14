"""
OSM TO LULC - Modules to deal with vetorial data
"""

import datetime as dt

from glass.cons.otol import DB_SCHEMA, OSM_TABLES, OSM_PK, OSM_GEOM
from glass.cons.otol import OTOL_MODULE, OTOL_GEOM, OTOL_LULC
from glass.gp.gen.sql import st_dissolve
from glass.prop.sql import row_num
from glass.gp.prox.bfing.sql import st_buffer


def module_1(tags, osmdb, epsg, gpkg, layer):
    """
    Simple Selection of OSM Features and
    geometric generalization (aggregation)
    """

    time_a = dt.datetime.now().replace(microsecond=0)

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    # Get tags related with module one
    tdf = tags[tags[modcol] == 'selection'].copy(deep=True)

    tdf.loc[:, valcol] = 'tcls.' + tdf[keycol] + "='" + tdf[valcol] + "'"

    geom_col = (
        "CASE "
            f"WHEN ST_IsValid(ST_Transform({OSM_GEOM}, {epsg})) "
            f"THEN ST_Transform({OSM_GEOM}, {epsg}) "
            f"ELSE ST_MakeValid(ST_Transform({OSM_GEOM}, {epsg})) "
        f"END AS {OTOL_GEOM}"
    )

    time_b = dt.datetime.now().replace(microsecond=0)

    if not tdf.shape[0]:
        # No tags, Nothing to do
        return None, {0 : ('get_tags', time_b - time_a)}
    
    # Get classes inside this module
    lulcs = tdf[lulcol].unique()

    qs = []
    # For each LULC Class, Get a query to select features
    # to be related with that class
    for lcls in lulcs:
        # Get only the keys and values of this class
        clsdf = tdf[tdf[lulcol] == lcls]

        # Create a query to select the polygons
        # with these keys and values
        q = (
            f"SELECT {OSM_PK}, 'selection' AS {OTOL_MODULE}, "
            f"{lcls} AS {OTOL_LULC}, {geom_col} "
            f"FROM {OSM_TABLES['polygons']} AS tcls "
            f"WHERE {str(clsdf[valcol].str.cat(sep=' OR '))}"
        )

        qs.append(q)
    
    # Get final Query
    # Union ALL of each query in qs
    # (one query by class)
    fq = " UNION ALL ".join(qs)
    time_c = dt.datetime.now().replace(microsecond=0)

    # Check if we have interest data
    nrows = row_num(osmdb, fq, api='psql')

    time_d = dt.datetime.now().replace(microsecond=0)

    if not nrows:
        return None, {
            0 : ('get_tags', time_b - time_a),
            1 : ('get_queries', time_c - time_b),
            2 : ('count_rows', time_d - time_c)
        }
    
    # Dissolve and export
    _out = st_dissolve(
        osmdb, f"({fq}) AS mtbl", OTOL_GEOM, gpkg,
        diss_cols=OTOL_LULC, outTblIsFile=True,
        olyr=layer, api='psql', multipart=None
    )

    time_e = dt.datetime.now().replace(microsecond=0)

    return layer, {
        0 : ('get_tags', time_b - time_a),
        1 : ('get_queries', time_c - time_b),
        2 : ('count_rows', time_d - time_c),
        3 : ('select_dissolve_export', time_e - time_d)
    }


def module_2(tags, osmdb, epsg, gpkg, layer):
    """
    Roads processing using PostGIS and Table Views based approach
    """

    from glass.gp.prox.sql import st_near
    from glass.sql.q       import exec_write_q

    time_a = dt.datetime.now().replace(microsecond=0)

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    # Get tags related with module one
    tdf = tags[tags[modcol] == 'roads'].copy(deep=True)

    tdf.loc[:, valcol] = 'tcls.' + tdf[keycol] + "='" + tdf[valcol] + "'"

    geom_col = f"ST_Transform({OSM_GEOM}, {epsg}) AS {OTOL_GEOM}"

    geom_ply = (
        "CASE "
            f"WHEN ST_IsValid(ST_Transform({OSM_GEOM}, {epsg})) "
            f"THEN ST_Transform({OSM_GEOM}, {epsg}) "
            f"ELSE ST_MakeValid(ST_Transform({OSM_GEOM}, {epsg})) "
        f"END AS {OTOL_GEOM}"
    )

    bfcol = DB_SCHEMA['OSM_LULC']['BUFFER']

    tdf[bfcol] = tdf[bfcol].astype(int)

    # Building's table
    build_tbl = (
        f"SELECT building, {geom_ply} "
        f"FROM {OSM_TABLES['polygons']} "
        "WHERE building IS NOT NULL"
    )

    # New tables to be created
    troads, tbuild = 'tbl_roads', 'tbl_build'

    time_b = dt.datetime.now().replace(microsecond=0)

    if not tdf.shape[0]:
        # No tags, Nothing to do
        return None, {0 : ('get_tags', time_b - time_a)}
    
    # Get classes inside this module
    lulcs = tdf[lulcol].unique()

    # For each LULC Class, Get a query to select features
    # to be related with that class
    qs = []
    for lcls in lulcs:
        # Get only the keys and values of this class
        clsdf = tdf[tdf[lulcol] == lcls]

        # Create a query to select these keys and values
        dists = clsdf[bfcol].unique()

        for d in dists:
            subclsdf = clsdf[clsdf[bfcol] == d]

            q = (
                f"SELECT {OSM_PK}, 'roads' AS {OTOL_MODULE}, "
                f"{lcls} AS {OTOL_LULC}, {geom_col}, "
                "CASE "
                    "WHEN width IS NOT NULL AND width ~ '^[0-9]+$' AND "
                    "CAST(width AS numeric) < 20 "
                    "THEN CAST(round(CAST(width AS numeric), 0) AS integer) "
                    "ELSE CASE "
                        "WHEN lanes IS NOT NULL AND lanes ~ '^[0-9]+$' "
                        "THEN CAST(round((CAST(lanes AS integer) * 3), 0) AS integer) "
                        f"ELSE {d} "
                    "END "
                f"END AS {bfcol} "
                f"FROM {OSM_TABLES['lines']} AS tcls "
                f"WHERE {str(subclsdf[valcol].str.cat(sep=' OR '))}"
            )

            qs.append(q)
    
    # Get final Query
    # Union ALL of each query in qs
    # (one query by class and buffer distance)
    fq = " UNION ALL ".join(qs)

    # Count number of roads
    n_roads = row_num(osmdb, fq, api='psql')

    time_c = dt.datetime.now().replace(microsecond=0)

    if not n_roads:
        return None, {
            0 : ('get_tags', time_b - time_a),
            1 : ('count_rows_roads', time_c - time_b)
        }

    # Create a new table only with the roads 
    # - Create Primary Key and add a index to geometry
    # to make the procedure faster
    qs = [(
        f"CREATE TABLE {troads} AS {fq}"
    ), (
        f"ALTER TABLE {troads} ADD CONSTRAINT "
        f"{troads}_pk PRIMARY KEY ({OSM_PK})"
    ), (
        f"CREATE INDEX {troads}_geom_idx ON {troads} "
        f"USING gist ({OTOL_GEOM})"
    )]

    # Check if there are buildings or not
    n_build = row_num(osmdb, build_tbl, api='psql')
    time_d = dt.datetime.now().replace(microsecond=0)

    # If we have buildings, create also a table
    # with all the buildings
    if n_build:
        qs.extend([
            f"CREATE TABLE {tbuild} AS {build_tbl}",
            f"CREATE INDEX {tbuild}_geom_idx ON {tbuild} USING gist ({OTOL_GEOM})"
        ])
    
    exec_write_q(osmdb, qs, api='psql')
    time_e = dt.datetime.now().replace(microsecond=0)

    # If we have buildings, lets find buffer distance
    # based on the distance between roads and buildings
    if n_build:
        qroads = st_near(
            osmdb, troads, OTOL_GEOM,
            tbuild, OTOL_GEOM,
            intbl_pk=OSM_PK,
            until_dist="12", near_col="dist_near"
        )

        qroads = (
            f"(SELECT {OSM_PK}, {OTOL_MODULE}, {OTOL_LULC}, {OTOL_GEOM}, "
            "CASE "
                "WHEN dist_near >= 1 AND dist_near <= 12 "
                "THEN CAST(round(CAST(dist_near AS numeric), 0) AS integer) "
                f"ELSE {bfcol} "
            f"END AS {bfcol} "
            f"FROM ({qroads}) AS ffroads)"
        )
    
    else:
        qroads = troads
    
    # Execute buffer
    bf_roads = st_buffer(
        osmdb, qroads, bfcol, OTOL_GEOM, output=gpkg,
        outTblIsFile=True, cols_select=OTOL_LULC, dissolve="SEL",
        olyr=layer
    )
    time_f = dt.datetime.now().replace(microsecond=0)

    return layer, {
        0 : ('get_tags', time_b - time_a),
        1 : ('count_rows_roads', time_c - time_b),
        2 : ('count_rows_build', time_d - time_c),
        3 : ('create_roads_build_tables', time_e - time_d),
        4 : ('near_and_buffer', time_f - time_e)
    }


def module_3_and_4(tags, osmdb, epsg, gpkg, layer, upper=True):
    """
    Select features with area upper/lower than.
    
    A field with threshold is needed in the database.
    """

    time_a = dt.datetime.now().replace(microsecond=0)

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    o = ">" if upper else "<="
    module = 'area_upper' if upper else 'area_lower'

    # Get tags related with module one
    tdf = tags[tags[modcol] == module].copy(deep=True)

    tdf.loc[:, valcol] = 'tcls.' + tdf[keycol] + "='" + tdf[valcol] + "'"

    geom_col = (
        "CASE "
            f"WHEN ST_IsValid(ST_Transform({OSM_GEOM}, {epsg})) "
            f"THEN ST_Transform({OSM_GEOM}, {epsg}) "
            f"ELSE ST_MakeValid(ST_Transform({OSM_GEOM}, {epsg})) "
        f"END AS {OTOL_GEOM}"
    )

    area_col = DB_SCHEMA['OSM_LULC']['AREA']

    tdf[area_col] = tdf[area_col].astype(int)

    time_b = dt.datetime.now().replace(microsecond=0)

    if not tdf.shape[0]:
        # No tags, Nothing to do
        return None, {0 : ('get_tags', time_b - time_a)}
    
    # Get classes inside this module
    lulcs = tdf[lulcol].unique()

    # For each LULC Class, Get a query to select features
    # to be related with that class
    qs = []
    for lcls in lulcs:
        # Get only the keys and values of this class
        clsdf = tdf[tdf[lulcol] == lcls]

        # Create a query to select these keys and values
        ths = clsdf[area_col].unique()

        for t in ths:
            subclsdf = clsdf[clsdf[area_col] == t]

            q = (
                f"SELECT {OSM_PK}, '{module}' AS {OTOL_MODULE}, "
                f"{lcls} AS {OTOL_LULC}, {geom_col} "
                f"FROM {OSM_TABLES['polygons']} AS tcls "
                f"WHERE ({str(subclsdf[valcol].str.cat(sep=' OR '))}) "
                f"AND ST_Area(ST_MakeValid(ST_Transform({OSM_GEOM}, {epsg}))) {o} "
                f"{t}"
            )

            qs.append(q)
    
    # Get final Query
    # Union ALL of each query in qs
    # (one query by class and area threshold)
    fq = " UNION ALL ".join(qs)

    # Check if we have data
    nrows = row_num(osmdb, fq, api='psql')
    time_c = dt.datetime.now().replace(microsecond=0)

    if not nrows:
        return None, {
            0 : ('get_tags', time_b - time_a),
            1 : ('count_rows', time_c - time_b)
        }
    
    # Dissolve
    out_ = st_dissolve(
        osmdb, f"({fq}) AS mtbl", OTOL_GEOM,
        gpkg, diss_cols=OTOL_LULC, outTblIsFile=True,
        api='psql', multipart=None, olyr=layer
    )

    time_d = dt.datetime.now().replace(microsecond=0)

    return layer, {
        0 : ('get_tags', time_b - time_a),
        1 : ('count_rows', time_c - time_b),
        2 : ('dissolve_export', time_d - time_c)
    }


def module_5(tags, osmdb, epsg, gpkg, layer):
    """
    Basic Buffer strategy
    """

    time_a = dt.datetime.now().replace(microsecond=0)

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    # Get tags related with module one
    tdf = tags[tags[modcol] == 'basic_buffer'].copy(deep=True)

    tdf.loc[:, valcol] = 'tcls.' + tdf[keycol] + "='" + tdf[valcol] + "'"

    geom_col = f"ST_Transform({OSM_GEOM}, {epsg}) AS {OTOL_GEOM}"

    bfcol = DB_SCHEMA['OSM_LULC']['BUFFER']

    tdf[bfcol] = tdf[bfcol].astype(int)

    time_b = dt.datetime.now().replace(microsecond=0)

    if not tdf.shape[0]:
        # No tags, Nothing to do
        return None, {0 : ('get_tags', time_b - time_a)}
    
    # Get classes inside this module
    lulcs = tdf[lulcol].unique()

    # For each LULC Class, Get a query to select features
    # to be related with that class
    qs = []
    for lcls in lulcs:
        # Get only the keys and values of this class
        clsdf = tdf[tdf[lulcol] == lcls]

        # Create a query to select these keys and values
        dists = clsdf[bfcol].unique()

        for d in dists:
            subclsdf = clsdf[clsdf[bfcol] == d]

            q = (
                f"SELECT {OSM_PK}, 'basic_buffer' AS {OTOL_MODULE}, "
                f"{lcls} AS {OTOL_LULC}, {geom_col}, "
                f"{d} AS {bfcol} "
                f"FROM {OSM_TABLES['lines']} AS tcls "
                f"WHERE {str(subclsdf[valcol].str.cat(sep=' OR '))}"
            )

            qs.append(q)
    
    # Get final Query
    # Union ALL of each query in qs
    # (one query by class and buffer distance)
    fq = " UNION ALL ".join(qs)

    # Count number of features
    nfeat = row_num(osmdb, fq, api='psql')

    time_c = dt.datetime.now().replace(microsecond=0)

    if not nfeat:
        return None, {
            0 : ('get_tags', time_b - time_a),
            1 : ('count_rows', time_c - time_b)
        }
    
    # Run Buffer
    res = st_buffer(
        osmdb, f"({fq})", bfcol, OTOL_GEOM, output=gpkg,
        outTblIsFile=True, cols_select=OTOL_LULC, dissolve="SEL",
        olyr=layer
    )

    time_d = dt.datetime.now().replace(microsecond=0)

    return layer, {
        0 : ('get_tags', time_b - time_a),
        1 : ('count_rows', time_c - time_b),
        2 : ('buffer_export', time_d - time_c)
    }


def module_6(tags, osmdb, epsg, gpkg, layer):
    """
    Replace buildings with tag yes using the info in the Points Layer
    
    Only used for URBAN ATLAS and CORINE LAND COVER
    """

    from glass.gp.ovl.sql import feat_within
    from glass.it.shp import dbtbl_to_shp

    time_a = dt.datetime.now().replace(microsecond=0)

    keycol = DB_SCHEMA["OSM_FEATURES"]["KEY"]
    valcol = DB_SCHEMA["OSM_FEATURES"]["VALUE"]
    lulcol = DB_SCHEMA['OSM_LULC']['LULCID']
    modcol = DB_SCHEMA['MODULES']['NAME']

    geom_pnt = f"ST_Transform({OSM_GEOM}, {epsg}) AS {OTOL_GEOM}"

    geom_ply = (
        "CASE "
            f"WHEN ST_IsValid(ST_Transform({OSM_GEOM}, {epsg})) "
            f"THEN ST_Transform({OSM_GEOM}, {epsg}) "
            f"ELSE ST_MakeValid(ST_Transform({OSM_GEOM}, {epsg})) "
        f"END AS {OTOL_GEOM}"
    )

    # Get tags related with this module
    dfs = {
        'pnt' : tags[
            (tags[modcol] == 'selection') &
            (tags[keycol] == 'building')
        ].copy(deep=True),
        'ply' : tags[tags[modcol] == 'buildings'].copy(deep=True)
    }

    for k in dfs:
        if not dfs[k].shape[0]:
            dfs[k] = None
            continue

        dfs[k].loc[:, valcol] = 'tcls.' + dfs[k][keycol] + "='" + dfs[k][valcol] + "'"

        tbl = OSM_TABLES['points'] if k == 'pnt' else OSM_TABLES['polygons']

        geom_col = geom_ply if k == 'ply' else geom_pnt

        # Get classes
        lulcs = dfs[k][lulcol].unique()

        # One query for each class
        qs = []
        for lcls in lulcs:
            # Get only the keys and values of this class
            clsdf = dfs[k][dfs[k][lulcol] == lcls]

            # Create a query to select the features
            # with these keys and values
            q = (
                f"SELECT {OSM_PK}, 'buildings' AS {OTOL_MODULE}, "
                f"{lcls} AS {OTOL_LULC}, {geom_col} "
                f"FROM {tbl} AS tcls "
                f"WHERE {str(clsdf[valcol].str.cat(sep=' OR '))}"
            )

            qs.append(q)
        
        dfs[k] = " UNION ALL ".join(qs)

    time_b = dt.datetime.now().replace(microsecond=0)

    if not dfs['ply']:
        # No tags in the polygons, Nothing to do
        return None, {0 : ('get_poly_tags', time_b - time_a)}
    
    # Count Polygon features
    nply = row_num(osmdb, dfs['ply'], api='psql')

    time_c = dt.datetime.now().replace(microsecond=0)

    if not nply:
        # No features in the polygons, Nothing to do
        return None, {
            0 : ('get_poly_tags', time_b - time_a),
            1 : ('count_poly', time_c - time_b)
        }
    
    # Check if we have tags and features in points
    npnt = None if not dfs['pnt'] else \
        row_num(osmdb, dfs['pnt'], api='psql')
    
    time_d = dt.datetime.now().replace(microsecond=0)
    
    if npnt:
        # Run feat Within
        fwres = feat_within(
            osmdb, f"({dfs['ply']})", OTOL_GEOM,
            f"({dfs['pnt']})", OTOL_GEOM,
            left_cols=[OSM_PK, OTOL_LULC, OTOL_MODULE],
            within_cols=[f"{OTOL_LULC} AS pnt_lulc"],
            join="LEFT", geom_col="left", geomname=OTOL_GEOM
        )

        fwres = (
            f"SELECT {OSM_PK}, {OTOL_GEOM}, {OTOL_MODULE}, "
            "CASE "
                "WHEN pnt_lulc IS NOT NULL "
                f"THEN pnt_lulc ELSE {OTOL_LULC} "
            f"END AS {OTOL_LULC} "
            f"FROM ({fwres}) AS fwith"
        )
    
    else:
        fwres = dfs['ply']
    
    # Export data
    dbtbl_to_shp(
        osmdb, fwres, OTOL_GEOM, gpkg, api="ogr2ogr",
        tableIsQuery=True, olyr=layer
    )

    time_e = dt.datetime.now().replace(microsecond=0)

    return layer, {
        0 : ('get_poly_tags', time_b - time_a),
        1 : ('count_poly', time_c - time_b),
        2 : ('count_pnts', time_d - time_c),
        3 : ('feat_within_export', time_e - time_d)
    }


def priority_rule(gpkg, lyr, rst, col, osm_db):
    """
    Apply priority rule v1.5
    """

    import datetime as dt
    import copy

    from glass.cons.otol  import OTOL_GEOM, classes_priority
    from glass.gp.ovl.sql import st_erase_opt
    from glass.gp.seg.sql import geomseg_to_newtbl
    from glass.it.db      import gpkg_lyr_attr_to_psql
    from glass.prop.prj   import get_epsg
    from glass.prop.sql   import row_num
    from glass.sql.q      import exec_write_q

    # Get EPSG
    epsg = get_epsg(rst)

    # Get Classes Priority
    order_cls = classes_priority(2)

    # Import data into the database
    table_cls = gpkg_lyr_attr_to_psql(gpkg, lyr, col, osm_db, 'tblcls')

    # Create segments table if necessary
    for cls in order_cls:
        cls['pk'] = 'fid'
        if not cls['bigbbox']: continue

        if cls['fid'] not in table_cls: continue
    
        table_cls[cls['fid']] = geomseg_to_newtbl(
            osm_db, table_cls[cls['fid']],
            'fid', 'geom', 'polygon', epsg,
            f"{table_cls[cls['fid']]}_seg",
            cols={'lulc' : 'integer', 'leg': 'text'},
            subdivide_factor=10
        )

        cls['pk'] = 'sid'
    
    # Go for erasing
    refname = copy.deepcopy(table_cls)

    for e in range(len(order_cls)):
        if e + 1 == len(order_cls): break

        if order_cls[e]['fid'] not in table_cls: continue

        for i in range(e+1, len(order_cls)):
            if order_cls[i]['fid'] not in table_cls: continue

            time_a = dt.datetime.now().replace(microsecond=0)

            table_cls[order_cls[i]['fid']] = st_erase_opt(
                osm_db,
                table_cls[order_cls[i]['fid']], 'fid',
                table_cls[order_cls[e]['fid']],
                "geom", "geom",
                otbl=f"{refname[order_cls[i]['fid']]}_{str(e)}"
            )

            time_b = dt.datetime.now().replace(microsecond=0)

            print((
                f'{table_cls[order_cls[i]["fid"]]} <-> '
                f'{table_cls[order_cls[e]["fid"]]} || {time_b - time_a}'
            ))
            print('---------------------------------')

            nrows = row_num(osm_db, table_cls[order_cls[i]['fid']], api='psql')

            if not nrows:
                del table_cls[order_cls[i]['fid']]
                continue

            # Create Geometry index for the new table
            qs = [(
                f"ALTER TABLE {table_cls[order_cls[i]['fid']]} ADD CONSTRAINT "
                f"{table_cls[order_cls[i]['fid']]}_pk PRIMARY KEY "
                f"({order_cls[i]['pk']})"
            ), (
                f"CREATE INDEX {table_cls[order_cls[i]['fid']]}_geom_idx ON "
                f"{table_cls[order_cls[i]['fid']]} "
                f"USING gist (geom)"
            )]

            exec_write_q(osm_db, qs, api='psql')

    return 1
