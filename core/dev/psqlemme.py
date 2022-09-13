"""
Write Emme files from GTFS in a PostgreSQL DB
"""


def write_emme_routes_file(conParam, DB_SCHEMA, dayToUse, lowerTimeInterval,
                           upperTimeInterval, EMME_FILE,
                           DefaultMode='b', OtherModes=None):
    """
    Write a Emme file (d221.in) with the information about the routes
    provided by an operator (e.g., SMTUC).
    Write route frequencies and stops.
    
    conParam = {
        "HOST" : "localhost", "PORT" : "5432", "PASSWORD" : "admin",
        "USER" : "postgres", "DATABASE" : "gtfs_carris"}
    
    DB_SCHEMA example:
    DB_SCHEMA = {
        "ROUTES" : {
            "TNAME"  : "routes", #TABLE NAME
            "ID"     : "route_id", # FIELD NAME
            "SHORT"  : "route_short_name", # FIELD NAME
            "LONG"   : "route_long_name", # FIELD NAME
            "AGENCY" : "agency_id" # FIELD NAME
        },
        "STOP_TIMES" : {
            "TNAME"     : "stop_times",
            "TRIP"      : "trip_id",
            "STOP"      : "stop_id",
            "SEQUENCE"  : "stop_sequence",
            "DEPARTURE" : "departure_time"
        },
        "TRIPS" : {
            "TNAME"   : "trips",
            "TRIP"    : "trip_id",
            "ROUTE"   : "route_id",
            "SERVICE" : "service_id"
        },
        "AGENCY" : {
            "TNAME" : "agency",
            "ID"    : "agency_id",
            "NAME"  : "agency_name"
        },
        "CALENDAR" : {
            "TNAME"   : "calendar_dates",
            "SERVICE" : "service_id",
            "DATE"    : "date"
        },
        "ROUTES_EXTRA" : { # Optional
            "TNAME" : "percursos_geom_v2",
            "ROUTE" : "fid_percurso",
            "STOP"  : "paragem",
            "ORDER" : "ordem"
        },
        "TRIP_VEHICLE" : { # Optional
            "TNAME" : "veiculo_by_circ_1801",
            "TRIP"  : "trip_id"
            "CAR"   : "id_emme"
        }
    }
    
    dayToUse example: dayToUse = "20180222" # 22 February 2018
    Interval example:
    upperInterval = "2018-02-22 10:00:00"
    lowerInterval = "2018-02-22 08:00:00"
    
    EMME_FILE is the path to the output file
    
    OtherModes is a dict to specific modes of transportation
    OtherModes = {
        short_name : 'e' # for electric
    }
    The DefaultMode is Bus
    """
    
    import pandas
    import codecs
    import unicodedata
    from glass.fm.psql import sql_query
    
    # Get all agencies
    agencies = pandas.DataFrame(sql_query(conParam,
        "SELECT {}, {} FROM {}".format(
            DB_SCHEMA["AGENCY"]["ID"], DB_SCHEMA["AGENCY"]["NAME"],
            DB_SCHEMA["AGENCY"]["TNAME"]
        )
    ), columns=[
        DB_SCHEMA["AGENCY"]["ID"], DB_SCHEMA["AGENCY"]["NAME"]
    ]).values.tolist()
    
    DAY = lowerTimeInterval.split(" ")[0] + " "
    
    # SELECT ALL POSSIBLE TRIPS FROM GTFS
    SQL_ROUTES = (
        "SELECT MIN(fid) AS fid, MIN(long_name) AS long_name, "
        "{short_cod}, stops, stops_sequence, {agencyF}, "
        "COALESCE({short_cod}, '') || '|' || "
        "COALESCE(row_number() OVER(PARTITION BY {short_cod} "
        "ORDER BY {short_cod})) AS route_id, "
        "COUNT(stops) AS ncirc, "
        "("
            "((EXTRACT(hour FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) * 60) + "
            "EXTRACT(minute FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) + "
            "(EXTRACT(second FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) / 60)) / COUNT(stops)"
        ") AS frequencies, stop_emme "
        "FROM ("
            "SELECT {stoptripID} AS fid, {short_cod}, {agencyF}, "
            "MIN({long_cod}) AS long_name, "
            "array_agg({stopID} ORDER BY {stoptripID}, {stopSq}) AS stops, "
            "array_agg({stopSq} ORDER BY {stoptripID}, {stopSq}) AS stops_sequence, "
            "array_agg(stop_emme ORDER BY {stoptripID}, {stopSq}) AS stop_emme, "
            "MIN(departure_time) AS departure_time "
            "FROM ("
                "SELECT {stopTiTbl}.{stoptripID}, "
                "TO_TIMESTAMP('{dday}' || {stopTiTbl}.{dep_time}, "
                    "'YYYY-MM-DD HH24:MI:SS') AS departure_time, "
                "'1' || repeat('0', (5-LENGTH(CAST(CAST({stopTiTbl}.{stopID} "
                    "AS integer) AS text)))) || CAST(CAST({stopTiTbl}.{stopID} "
                    " AS integer) AS text) AS stop_emme, "
                "{stopTiTbl}.{stopID}, {stopTiTbl}.{stopSq}, "
                "foo.{short_cod}, foo.{long_cod}, "
                "foo.{agencyF} FROM {stopTiTbl} INNER JOIN ("
                    "SELECT {tripsTbl}.{tripID}, {routeT}.{short_cod}, "
                    "{routeT}.{agencyF}, {routeT}.{long_cod} FROM {tripsTbl} "
                    "INNER JOIN {routeT} "
                    "ON {tripsTbl}.{tripRoID} = {routeT}.{routeID} "
                    "INNER JOIN {calenTbl} "
                    "ON {tripsTbl}.{tripServ} = {calenTbl}.{calenServ} "
                    "WHERE {calenTbl}.{calenDate} = {day}"
                ") AS foo ON {stopTiTbl}.{stoptripID} = foo.{tripID}"
            ") AS stops "
            "GROUP BY {stoptripID}, {short_cod}, {agencyF} "
            "ORDER BY {stoptripID}, {short_cod}"
        ") AS stops2 "
        "WHERE departure_time >= "
        "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS') "
        "AND departure_time < "
        "TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') "
        "GROUP BY {short_cod}, stops, stops_sequence, {agencyF}, stop_emme "
        "ORDER BY {short_cod}"
    ).format(
        short_cod  = DB_SCHEMA["ROUTES"]["SHORT"],
        agencyF    = DB_SCHEMA["ROUTES"]["AGENCY"],
        routeT     = DB_SCHEMA["ROUTES"]["TNAME"],
        routeID    = DB_SCHEMA["ROUTES"]["ID"],
        long_cod   = DB_SCHEMA["ROUTES"]["LONG"],
        stoptripID = DB_SCHEMA["STOP_TIMES"]["TRIP"],
        stopID     = DB_SCHEMA["STOP_TIMES"]["STOP"],
        stopSq     = DB_SCHEMA["STOP_TIMES"]["SEQUENCE"],
        stopTiTbl  = DB_SCHEMA["STOP_TIMES"]["TNAME"],
        dep_time   = DB_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        tripsTbl   = DB_SCHEMA["TRIPS"]["TNAME"],
        tripID     = DB_SCHEMA["TRIPS"]["TRIP"],
        tripRoID   = DB_SCHEMA["TRIPS"]["ROUTE"],
        tripServ   = DB_SCHEMA["TRIPS"]["SERVICE"],
        calenTbl   = DB_SCHEMA["CALENDAR"]["TNAME"],
        calenServ  = DB_SCHEMA["CALENDAR"]["SERVICE"],
        calenDate  = DB_SCHEMA["CALENDAR"]["DATE"],
        upInt      = upperTimeInterval,
        lwInt      = lowerTimeInterval,
        day        = dayToUse,
        dday       = DAY
    )
    
    colsDf = [
        "fid", "long_name", DB_SCHEMA["ROUTES"]["SHORT"], "stops",
        "stops_sequence", DB_SCHEMA["ROUTES"]["AGENCY"], "route_id",
        "ncirc", "frequencies", "stops_emme"
    ]
    
    # Get route id from other table not in GTFS Format
    if "ROUTES_EXTRA" in DB_SCHEMA.keys():
        SQL_ROUTES = (
            "SELECT tbl.*, rinfo.{r} "
            "FROM ({_q}) AS tbl "
            "INNER JOIN ("
                "SELECT {r}, "
                "array_agg({stop_} ORDER BY {order_}) AS stops, "
                "array_agg({order_} ORDER BY {order_}) AS stops_order "
                "FROM {rt} GROUP BY {r}"
            ") AS rinfo "
            "ON tbl.stops = rinfo.stops AND "
            "tbl.stops_sequence = rinfo.stops_order"
        ).format(
            _q     = SQL_ROUTES,
            r      = DB_SCHEMA["ROUTES_EXTRA"]["ROUTE"],
            stop_  = DB_SCHEMA["ROUTES_EXTRA"]["STOP"],
            order_ = DB_SCHEMA["ROUTES_EXTRA"]["ORDER"],
            rt     = DB_SCHEMA["ROUTES_EXTRA"]["TNAME"]
        )
        
        colsDf.append(DB_SCHEMA["ROUTES_EXTRA"]["ROUTE"])
        
        ROUTE_ID = DB_SCHEMA["ROUTES_EXTRA"]["ROUTE"]
    
    else:
        ROUTE_ID = "route_id"
    
    # Get vehicle type from other table not in GTFS Format
    if "TRIP_VEHICLE" in DB_SCHEMA.keys():
        SQL_ROUTES = (
            "SELECT tbll.*, {vt}.{vehi} "
            "FROM ({_q}) AS tbll "
            "INNER JOIN {vt} ON "
            "tbll.fid = {vt}.{tripid}"
        ).format(
            _q     = SQL_ROUTES,
            vt     = DB_SCHEMA["TRIP_VEHICLE"]["TNAME"],
            vehi   = DB_SCHEMA["TRIP_VEHICLE"]["CAR"],
            tripid = DB_SCHEMA["TRIP_VEHICLE"]["TRIP"]
        )
        
        colsDf.append(DB_SCHEMA["TRIP_VEHICLE"]["CAR"])
        
        VEHICLE_ID = DB_SCHEMA["TRIP_VEHICLE"]["CAR"]
    
    else:
        SQL_ROUTES = (
            "SELECT tbll.*, 5 AS vehicle "
            "FROM ({}) AS tbll"
        ).format(SQL_ROUTES)
        
        colsDf.append("vehicle")
        VEHICLE_ID = "vehicle"
    
    all_routes = pandas.DataFrame(
        sql_query(conParam, SQL_ROUTES), columns=colsDf)
    
    # Sanitize routes frequencies strings
    all_routes["frequencies"]  = all_routes["frequencies"].round(2)
    all_routes["frequencies"]  = all_routes["frequencies"].astype(str)
    
    all_routes["freq_decimal"] = all_routes["frequencies"].str.split(pat='.')
    all_routes["freq_decimal"] = all_routes["freq_decimal"].str[-1]
    all_routes["freq_len"]     = all_routes["freq_decimal"].map(str).apply(len)
    
    all_routes.loc[all_routes["freq_len"] == 1, "frequencies"] = \
        all_routes["frequencies"] + "0"
    
    # Sanitize stops column
    all_routes["stops_emme"] = all_routes["stops_emme"].astype(str)
    all_routes["stops_emme"] = all_routes["stops_emme"].str.replace(',', '')
    all_routes["stops_emme"] = all_routes["stops_emme"].str.replace('[', '')
    all_routes["stops_emme"] = all_routes["stops_emme"].str.replace(']', '')
    all_routes["stops_emme"] = all_routes["stops_emme"].str.replace('L', '')
    all_routes["stops_emme"] = all_routes["stops_emme"].str.replace('\'', '')
    
    # Sanitize long_name column
    all_routes["long_name"] = all_routes["long_name"].str.replace(' ', '_')
    all_routes["long_name"] = all_routes["long_name"].str.replace('.', '_')
    all_routes["long_name"] = all_routes["long_name"].str.replace('-', '_')
    all_routes["long_name"] = all_routes["long_name"].str.replace('/', '')
    all_routes["long_name"] = all_routes["long_name"].str.replace('__', '_')
    all_routes["long_name"] = all_routes["long_name"].str.replace('(', '')
    all_routes["long_name"] = all_routes["long_name"].str.replace(')', '')
    all_routes["long_name"] = all_routes["long_name"].str.replace('__', '_')
    
    # Sanitize Vehicle Type
    all_routes[VEHICLE_ID] = all_routes[VEHICLE_ID].astype(str)
    
    # Produce mode column
    all_routes["mode"] = DefaultMode
    if OtherModes:
        for md in OtherModes:
            all_routes.loc[
                all_routes[DB_SCHEMA["ROUTES"]["SHORT"]] == md, "mode"
            ] = OtherModes[md]
    
    # Concat interest rows
    all_routes["rbase"] = "'" + all_routes[ROUTE_ID] + "' " + \
        all_routes["mode"] + " " + all_routes[VEHICLE_ID] + " " + \
        all_routes["frequencies"] + " 40.00 '" + \
        all_routes["long_name"].str[:21] + "' 0 0 0"
    
    all_routes["rpath"] = "path=no"
    all_routes["rlay"]  = "lay=3"
    
    with codecs.open(EMME_FILE, 'w', encoding='utf-8') as txt:
        txt.write(u"t lines\n")
        
        for a in range(len(agencies)):
            ag_routes = all_routes[
                all_routes[DB_SCHEMA["ROUTES"]["AGENCY"]] == agencies[a][0]
            ]
            
            base  = ag_routes["rbase"].values.tolist()
            path  = ag_routes["rpath"].values.tolist()
            lay   = ag_routes["rlay"].values.tolist()
            stops = ag_routes["stops_emme"].values.tolist()
            
            txt.write(u"c\nc {}\nc\n".format(unicode(agencies[a][1], 'utf-8')))
            
            for r in range(len(base)):
                __base = unicode(unicodedata.normalize(
                    'NFKD', unicode(base[r], 'utf-8')).encode(
                        'ascii', 'ignore'), 'utf-8')
                
                __stops = stops[r].split(' ')
                _stops_ = [__stops[i:i+3] for i in range(0, len(__stops), 3)]
                
                towrite = u"a {}\n {} {}\n {}{}{}{}".format(
                    __base, path[r], " ".join(_stops_[0]),
                    "\n ".join([" ".join(s) for s in _stops_[1:]]),
                    "\n " if len(_stops_[1:]) else "",
                    lay[r],
                    "" if a + i == len(agencies) and r + 1 == len(base) else "\n"
                )
                
                txt.write(towrite)
        txt.close()
    
    return all_routes


def roads_to_emme(stopsFile, stopsId, rdvFile, rdvId,
                  rdvModes, travelCol, rdvType, rdvLanes,
                  centroids, cntrId,
                  conParam, srs_epsg, outfile,
                  date="18-07-02 11:30"):
    """
    Roads Network to EMME File (d211.in)
    
    Write a Emme file with the information about the nodes and arcs
    of one network
    """
    
    import codecs
    from glass.to.psql           import shp_to_psql_tbl
    from glass.fm.psql           import query_to_df
    from glass.cpu.psql.mng      import create_db
    from glass.cpu.psql.mng.fld  import cols_name
    from glass.sql.q   import q_to_ntbl
    from glass.cpu.psql.mng.geom import add_endpoints_to_table
    from glass.cpu.psql.mng.geom import check_endpoint_ispoint
    
    # Sanitize columns fields
    stopsId  = stopsId.lower() ; rdvId     = rdvId.lower()
    rdvModes = rdvModes.lower(); travelCol = travelCol.lower()
    rdvType  = rdvType.lower() ; cntrId    = cntrId.lower()
    
    # Create new Database
    create_db(conParam, conParam["DB"], overwrite=True)
    conParam["DATABASE"] = conParam["DB"]
    
    # Send data to PostgreSQL
    tbl_stops = shp_to_psql_tbl(conParam, stopsFile, srs_epsg)
    tbl_rdv   = shp_to_psql_tbl(conParam,   rdvFile, srs_epsg)
    tbl_centr = shp_to_psql_tbl(conParam, centroids, srs_epsg)
    
    # Get nodes in rdv - Add Start/End Point to table
    rdvTbl = add_endpoints_to_table(
        conParam, tbl_rdv, "rdv_endpnt", idCol=rdvId,
        startCol="start_node", endCol="end_node"
    )
    
    # See which nodes are stops
    rdvTbl = check_endpoint_ispoint(
        conParam, rdvTbl, tbl_stops, "rdv_endpnt_v2",
        "start_node", "end_node", stopsId, pntGeom="geom"
    )
    
    # See if there are nodes related with stops in the same location
    # If that were the case, group by and mantain the first stop code
    # (alphabetic order)
    rdvTbl = q_to_ntbl(conParam, "endpnt_rdv_v3", (
        "SELECT * "
        "FROM ("
            "SELECT {cols}, "
            "first_value(start_id) OVER ("
                "PARTITION BY {rdvid} ORDER BY start_id) AS start_id, "
            "first_value(end_id) OVER ("
                "PARTITION BY {rdvid} ORDER BY end_id) AS end_id "
            "FROM {tbl}"
        ") AS foo "
        "GROUP BY {cols}, start_id, end_id"
    ).format(
        cols = ", ".join([c for c in cols_name(
            conParam, rdvTbl) if c != 'start_id' and c != 'end_id']),
        rdvid=rdvId, tbl=rdvTbl
    ))
    
    # Get real nodes table
    _q = (
        "SELECT {_rdvId}, "
        "CASE WHEN n = 1 THEN 'start' ELSE 'end' END AS nodet, "
        "CASE WHEN n = 1 THEN start_node ELSE end_node END AS node, "
        "CASE WHEN n = 1 THEN start_isstop ELSE end_isstop END AS isstop, "
        "CASE WHEN n = 1 THEN start_id ELSE end_id END AS stop_id "
        "FROM ("
            "SELECT *, row_number() OVER (PARTITION BY {_rdvId}) AS n "
            "FROM ("
                "SELECT * FROM {rdvTbl} AS foo1 "
                "UNION ALL "
                "SELECT * FROM {rdvTbl} AS foo2"
            ") AS foo"
        ") AS nodest"
    ).format(_rdvId=rdvId, rdvTbl=rdvTbl)
    
    q = (
        "SELECT x, y, isstop, stop_id, "
        "array_agg({_rdvId} ORDER BY {_rdvId}) AS {_rdvId}, "
        "array_agg(nodet ORDER BY {_rdvId}) AS nodet "
        "FROM ("
            "SELECT CAST(((round(CAST(ST_X(node) AS numeric), 4))*10000) "
                "AS integer) AS x, "
            "CAST(((round(CAST(ST_Y(node) AS numeric), 4)) * 10000) "
                "AS integer) AS y, "
            "isstop, stop_id, {_rdvId}, nodet FROM ({nodesq}) AS noq"
        ") AS foa "
        "GROUP BY x, y, isstop, stop_id"
    ).format(nodesq=_q, _rdvId=rdvId)
    
    realNodes = q_to_ntbl(conParam, "nodes_pnt", q)
    
    # Get nodes ID
    realNodes = q_to_ntbl(conParam, "nodes_wid", (
        "SELECT round((x / 10000.0), 4) AS x, "
        "round((y / 10000.0), 4) AS y, "
        "CASE WHEN len IS NULL THEN node_id ELSE len END AS node_id, "
        "0 AS iscenter, "
        "{_rdvId}, nodet FROM ("
            "SELECT x, y, {_rdvId}, nodet, "
            "CAST((row_number() OVER (PARTITION BY stop_id) + 20000) "
                "AS text) AS node_id, "
            "'1' || repeat('0', (5-LENGTH(CAST(CAST(stop_id AS integer) "
                "AS text)))) || CAST(CAST(stop_id AS integer) AS text) AS len "
            "FROM {t}"
        ") AS foo"
    ).format(t=realNodes, _rdvId=rdvId))
    
    # Add centroids to nodes Table
    realNodes = q_to_ntbl(conParam, "nodes_wid_v2", (
        "SELECT * FROM {t} UNION ALL "
        "SELECT round(CAST(ST_X(geom) AS numeric), 4) AS x, "
        "round(CAST(ST_Y(geom) AS numeric), 4) AS y, "
        "CAST({cntId} AS text) AS node_id, 1 AS iscenter, "
        "ARRAY[CAST(0 AS bigint)] AS cat, ARRAY['none'] AS nodet "
        "FROM {cntTbl}"
    ).format(
        t=realNodes, cntId=cntrId, cntTbl=tbl_centr
    ))
    
    # Get Arcs Table
    arcsTbl = q_to_ntbl(conParam, "arcs", (
        "SELECT jst.st_id AS start_id, jen.en_id AS end_id, main.dist AS dist, "
        "main.{modeCol}, main.{travel}, main.{rdtype}, main.{rdLanes} FROM ("
            "SELECT "
            "CAST(((round(CAST(ST_X(start_node) AS numeric), 4)) * 10000) "
                "AS bigint) AS start_x, "
            "CAST(((round(CAST(ST_Y(start_node) AS numeric), 4)) * 10000) "
                "AS bigint) AS start_y, "
            "CAST(((round(CAST(ST_X(end_node) AS numeric), 4)) * 10000) "
                "AS bigint) AS end_x, "
            "CAST(((round(CAST(ST_Y(end_node) AS numeric), 4)) * 10000) "
                "AS bigint) AS end_y, "
            "round(CAST((ST_Length(geom) / 1000) AS numeric), 2) AS dist, "
            "{modeCol}, {travel}, {rdLanes}, "
            "CAST({rdtype} AS text) AS {rdtype} FROM {rdvT}"
        ") AS main INNER JOIN ("
            "SELECT CAST(((round(CAST(x AS numeric), 4)) * 10000) "
                "AS bigint) AS st_x, "
            "CAST(((round(CAST(y AS numeric), 4)) * 10000) "
                "AS bigint) AS st_y, "
            "node_id AS st_id FROM {nodesT}"
        ") AS jst "
        "ON main.start_x = jst.st_x AND main.start_y = jst.st_y "
        "INNER JOIN ("
            "SELECT CAST(((round(CAST(x AS numeric), 4)) * 10000) "
                "AS bigint) AS en_x, "
            "CAST(((round(CAST(y AS numeric), 4)) * 10000) "
                "AS bigint) AS en_y, "
            "node_id AS en_id FROM {nodesT}"
        ") AS jen "
        "ON main.end_x = jen.en_x AND main.end_y = jen.en_y"
    ).format(
        rdvT   = rdvTbl   , nodesT = realNodes, modeCol = rdvModes,
        travel = travelCol, rdtype = rdvType  , rdLanes = rdvLanes
    ))
    
    # Nodes to Pandas
    nodesDf = query_to_df(conParam, "SELECT * FROM {}".format(realNodes))
    
    # Arcs to Pandas
    arcsDf = query_to_df(conParam, "SELECT * FROM {}".format(arcsTbl))
    
    # Prepare Nodes to be written
    nodesDf.loc[nodesDf.iscenter == 1, "iscenter"] = 'a*'
    nodesDf.loc[nodesDf.iscenter == 0, "iscenter"] = 'a '
    
    def add_wspaces(df, col, left=True):
        df["len_id"] = df[col].astype(str).str.len()
    
        max_len = df.loc[df["len_id"].idxmax()].len_id
    
        df.len_id = max_len - df.len_id
    
        df["ws"] = " "
        df.ws = df.ws.str.repeat(df.len_id)
    
        if left:
            df[col] = df.ws + df[col].astype(str)
        else:
            df[col] = df[col].astype(str) + df.ws
    
        df.drop(["ws", "len_id"], axis=1, inplace=True)
    
        return df
    
    nodesDf = add_wspaces(nodesDf, "node_id")
    
    nodesDf.x = nodesDf.x.astype(int)
    nodesDf.y = nodesDf.y.astype(int)
    
    nodesDf = add_wspaces(nodesDf, "x")
    nodesDf = add_wspaces(nodesDf, "y")
    
    col4 = "      0"
    col5 = "      0"
    col6 = "      0"
    col7 = "0000"
    
    # Column with data to be written
    nodesDf["lnh"] = nodesDf.iscenter + " " + nodesDf.node_id + " " + \
        nodesDf.x + " " + nodesDf.y + " " + col4 + " " + col5 + " " + \
        col6 + " " + col7
    
    # Prepare Arcs to be written
    # Fix To-From
    arcsDf.loc[arcsDf[travelCol] == "T", "start_id_fix"] = arcsDf.end_id
    arcsDf.loc[arcsDf[travelCol] != "T", "start_id_fix"] = arcsDf.start_id
    arcsDf.loc[arcsDf[travelCol] == "T", "end_id_fix"]   = arcsDf.start_id
    arcsDf.loc[arcsDf[travelCol] != "T", "end_id_fix"]   = arcsDf.end_id
    
    # Duplicate both travelling
    bothDf = arcsDf.loc[arcsDf[travelCol] == "B"]
    bothDf["start_id_fix"] = bothDf.end_id
    bothDf["end_id_fix"]   = bothDf.start_id
    
    # Add duplicates to main Arcs DataFrame
    arcsDf = arcsDf.append(bothDf, ignore_index=True)
    
    arcsDf.drop(["start_id", "end_id"], axis=1, inplace=True)
    arcsDf.rename(columns={
        "start_id_fix" : "start_id", "end_id_fix" : "end_id"
    }, inplace=True)
    
    arcsDf = add_wspaces(arcsDf, "start_id")
    arcsDf = add_wspaces(arcsDf, "end_id")
    arcsDf = add_wspaces(arcsDf, "dist", left=None)
    arcsDf = add_wspaces(arcsDf, rdvModes, left=None)
    
    # Sanitize rdvType
    arcsDf[rdvType] = arcsDf[rdvType].astype(str)
    arcsDf["auxtype"] = arcsDf[rdvType].str[-1]
    
    # Sanitize Lanes Column
    arcsDf[rdvLanes] = arcsDf[rdvLanes].astype(int)
    arcsDf[rdvLanes] = arcsDf[rdvLanes].astype(str)
    arcsDf[rdvLanes] = arcsDf[rdvLanes] + ".0"
    
    # Prepare column with data to be written
    arcsDf["lnh"] = "a  " + arcsDf.start_id + "  " + arcsDf.end_id + "   " + \
        arcsDf.dist + " " + arcsDf[rdvModes] + (" " * 7) + \
        arcsDf[rdvType] + " "+ arcsDf[rdvLanes] + "   " + arcsDf.auxtype + \
        "       0       0       0"
    
    # Write file
    with codecs.open(outfile, "w", encoding='utf-8') as txt:
        txt.write((
            "c Emme Module:    2.14(v9.04)  "
            "Date: {}   "
            "User: EC98/TRENMO.....cm\n"
        ).format(date))
        
        txt.write((
            "c Project:        AML2018"
            "                         "
            "                            \n"
        ))
        txt.write((
            "c Scenario    1:  Cenario Base"
            "                              "
            "                  \n"
        ))
        
        # Write nodes
        txt.write("t nodes init\n")
        
        writeNodes = nodesDf["lnh"].values.tolist()
        
        for row in writeNodes:
            txt.write("{}\n".format(row))
        
        # Write links
        txt.write("\nt links init\n")
        
        writeLinks = arcsDf["lnh"].values.tolist()
        for row in writeLinks:
            txt.write("{}\n".format(row))
        
        txt.close()
    
    return outfile

