"""
ID Circulations using GTFS
"""


def list_trips(db, db_schema, gtfsDay, pgDay,
               lowerTimeInt=None, upperTimeInt=None):
    """
    Return a DataFrame with all Trips in GTFS
    
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
        }
    }
    
    dayToUse example: dayToUse = "20180222" # 22 February 2018
    Interval example:
    upperInterval = "10:00:00"
    lowerInterval = "08:00:00"
    """
    
    from glass.sql.q import q_to_obj
    
    if upperTimeInt and lowerTimeInt:
        upperTimeInt = "{} {}".format(pgDay, upperTimeInt)
        lowerTimeInt = "{} {}".format(pgDay, lowerTimeInt)
    
    SQL_ROUTES = (
        "SELECT MIN(fid) AS fid, MIN(long_name) AS long_name, "
        "{short_cod}, stops, stops_sequence, {agencyF}, "
        "COALESCE({short_cod}, '') || '|' || "
        "COALESCE(row_number() OVER(PARTITION BY {short_cod} "
        "ORDER BY {short_cod})) AS route_id, "
        "COUNT(stops) AS ncirc{freq} "
        "FROM ("
            "SELECT {stoptripID} AS fid, {short_cod}, {agencyF}, "
            "MIN({long_cod}) AS long_name, "
            "array_agg({stopID} ORDER BY {stoptripID}, {stopSq}) AS stops, "
            "array_agg({stopSq} ORDER BY {stoptripID}, {stopSq}) AS stops_sequence, "
            "MIN(departure_time) AS departure_time "
            "FROM ("
                "SELECT {stopTiTbl}.{stoptripID}, "
                "TO_TIMESTAMP('{dday}' || ' ' || {stopTiTbl}.{dep_time}, "
                    "'YYYY-MM-DD HH24:MI:SS') AS departure_time, "
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
        ") AS stops2 {whr}"
        "GROUP BY {short_cod}, stops, stops_sequence, {agencyF} "
        "ORDER BY {short_cod}"
    ).format(
        short_cod  = db_schema["ROUTES"]["SHORT"],
        agencyF    = db_schema["ROUTES"]["AGENCY"],
        routeT     = db_schema["ROUTES"]["TNAME"],
        routeID    = db_schema["ROUTES"]["ID"],
        long_cod   = db_schema["ROUTES"]["LONG"],
        stoptripID = db_schema["STOP_TIMES"]["TRIP"],
        stopID     = db_schema["STOP_TIMES"]["STOP"],
        stopSq     = db_schema["STOP_TIMES"]["SEQUENCE"],
        stopTiTbl  = db_schema["STOP_TIMES"]["TNAME"],
        dep_time   = db_schema["STOP_TIMES"]["DEPARTURE"],
        tripsTbl   = db_schema["TRIPS"]["TNAME"],
        tripID     = db_schema["TRIPS"]["TRIP"],
        tripRoID   = db_schema["TRIPS"]["ROUTE"],
        tripServ   = db_schema["TRIPS"]["SERVICE"],
        calenTbl   = db_schema["CALENDAR"]["TNAME"],
        calenServ  = db_schema["CALENDAR"]["SERVICE"],
        calenDate  = db_schema["CALENDAR"]["DATE"],
        day        = gtfsDay,
        dday       = pgDay,
        whr        = (
            "WHERE departure_time >= "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS') "
            "AND departure_time < "
            "TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') "
        ).format(
            upInt = upperTimeInt, lwInt = lowerTimeInt
        ) if upperTimeInt and lowerTimeInt else "",
        freq       = (
            ", (((EXTRACT(hour FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) * 60) + "
            "EXTRACT(minute FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) + "
            "(EXTRACT(second FROM TO_TIMESTAMP('{upInt}', 'YYYY-MM-DD HH24:MI:SS') - "
            "TO_TIMESTAMP('{lwInt}', 'YYYY-MM-DD HH24:MI:SS')) / 60)) / COUNT(stops)"
            ") AS frequencies"
        ).format(
            upInt = upperTimeInt, lwInt = lowerTimeInt
        ) if upperTimeInt and lowerTimeInt else ""
    )
    
    trips_df = q_to_obj(db, SQL_ROUTES, db_api='psql')
    
    return trips_df


def name_circulations(db, GTFS_SCHEMA, OTHER_SCHEMA, output,
                      other_db=None, serviceSchema=None,
                      routeIdColName=None, tripIdColName=None):
    """
    Get all circulations from GTFS and associate these circulations to
    other meta columns of other database
    
    GTFS_SCHEMA = {
        "TNAME"     : "stop_times",
        "TRIP"      : "trip_id",
        "STOP"      : "stop_id",
        "SEQUENCE"  : "stop_sequence",
        "DEPARTURE" : "departure_time"
    }
    
    OTHER_SCHEMA = {
        "TNAME"    : "percursos_geom_v2",
        "ROUTE"    : ["carreira", "variante", "sentido"],
        "SEQUENCE" : "ordem",
        "STOP"     : "paragem"
    }
    
    serviceSchema = {
        "TRIPS" : {
            "TNAME"   : "trips",
            "TRIP"    : "trip_id",
            "SERVICE" : "service_id"
        },
        "CALENDAR" : {
            "TNAME"   : "calendar_dates",
            "SERVICE" : "service_id",
            "DATE"    : "date"
        },
        "FILTER_DAY" : 20180308
    }
    """
    
    import os
    from glass.pys      import obj_to_lst
    from glass.sql.q import q_to_obj
    
    other_db = db if not other_db else other_db
    
    # Sanitize Route ID in Other Schema
    OTHER_SCHEMA_ROUTE = obj_to_lst(OTHER_SCHEMA["ROUTE"])
    
    if len(OTHER_SCHEMA_ROUTE) > 1:
        from glass.sql.col import txt_cols_to_col
        
        ROUTE_COL = routeIdColName if routeIdColName else "fid_route"
        
        txt_cols_to_col(
            other_db, OTHER_SCHEMA["TNAME"],
            OTHER_SCHEMA_ROUTE, "|", ROUTE_COL
        )
    
    else:
        ROUTE_COL = routeIdColName if routeIdColName else \
            OTHER_SCHEMA_ROUTE[0]
    
    """
    Get all circulations in GTFS and their start time
    """
    if serviceSchema:
        serviceSchema["FILTER_DAY"] = obj_to_lst(serviceSchema["FILTER_DAY"])
    
    where = "" if not serviceSchema else (
        " WHERE {} "
    ).format(
        " OR ".join([
            "{}.{} = {}".format(
                serviceSchema["CALENDAR"]["TNAME"],
                serviceSchema["CALENDAR"]["DATE"],
                d
            ) for d in serviceSchema["FILTER_DAY"]
        ])
    )
    
    injoinQ = "" if not serviceSchema else (
        "INNER JOIN ("
            "SELECT {tripsTbl}.{tripsTripId} "
            "FROM {tripsTbl} INNER JOIN {calenTbl} ON "
            "{tripsTbl}.{tripsServId} = {calenTbl}.{calenServId}{whr} "
            "GROUP BY {tripsTbl}.{tripsTripId}"
        ") AS trip_service ON {stopTimeTbl}.{stopTimeTrip} "
        "= trip_service.{tripsTripId} "
    ).format(
        tripsTbl     = serviceSchema["TRIPS"]["TNAME"],
        tripsTripId  = serviceSchema["TRIPS"]["TRIP"],
        tripsServId  = serviceSchema["TRIPS"]["SERVICE"],
        calenTbl     = serviceSchema["CALENDAR"]["TNAME"],
        calenServId  = serviceSchema["CALENDAR"]["SERVICE"],
        stopTimeTbl  = GTFS_SCHEMA["TNAME"],
        stopTimeTrip = GTFS_SCHEMA["TRIP"],
        whr          = where
    )
    
    newTripCol = tripIdColName if tripIdColName else GTFS_SCHEMA["TRIP"]
    
    Q = (
        "SELECT {stopTimesT}.{tripId} AS {newTrip}, "
        "array_agg({stopTimesT}.{stopId} "
            "ORDER BY {stopTimesT}.{tripId}, {stopTimesT}.{stopSq}) AS stops, "
        "array_agg({stopTimesT}.{stopSq} "
            "ORDER BY {stopTimesT}.{tripId}, {stopTimesT}.{stopSq}) AS stops_order, "
        "MIN({stopTimesT}.{depTime}) AS departure, "
        "MAX({stopTimesT}.{depTime}) AS depar_last_stop "
        "FROM {stopTimesT} {injoin}"
        "GROUP BY {stopTimesT}.{tripId}"
    ).format(
        tripId = GTFS_SCHEMA["TRIP"]     , stopId  = GTFS_SCHEMA["STOP"],
        stopSq = GTFS_SCHEMA["SEQUENCE"] , depTime = GTFS_SCHEMA["DEPARTURE"],
        stopTimesT = GTFS_SCHEMA["TNAME"], injoin  = injoinQ,
        newTrip = newTripCol
    )
    
    circ = q_to_obj(db, Q)
    
    """
    Get all routes metadata in the "Other Database/Table"
    """
    Q = (
        "SELECT {idRoute}, "
        "array_agg({stopF} ORDER BY {idRoute}, {stopSq}) AS stops, "
        "array_agg({stopSq} ORDER BY {idRoute}, {stopSq}) AS stops_order "
        "FROM {t} GROUP BY {idRoute}"
    ).format(
        idRoute = ROUTE_COL,
        stopF   = OTHER_SCHEMA["STOP"],
        stopSq  = OTHER_SCHEMA["SEQUENCE"],
        t       = OTHER_SCHEMA["TNAME"]
    )
    
    routes = q_to_obj(other_db, Q)
    
    def sanitizeDf(df, col):
        df[col] = df[col].astype(str)
        df[col] = df[col].str.replace('L', '')
        df[col] = df[col].str.replace(' ', '')
        df[col] = df[col].str.replace('[', '')
        df[col] = df[col].str.replace(']', '')
        
        return df
    
    circ   = sanitizeDf(  circ, "stops")
    routes = sanitizeDf(routes, "stops")
    
    newDf = circ.merge(routes, how='inner', left_on="stops", right_on="stops")
    
    if os.path.dirname(output):
        # Write XLS
        from glass.wt import obj_to_tbl
        
        obj_to_tbl(newDf, output)
    
    else:
        # Send to pgsql
        from glass.wt.sql import df_to_db
        
        df_to_db(db, newDf, output, api='psql')
    
    return output


def relate_busEntrances_circ(conGTFS_DB, conOTHER_DB, GTFS_SCHEMA,
                             OTHER_SCHEMA, GTFS_DAY, ENTRANCES_DAY,
                             OutTable, newDb="valbycirc_bd", NoErrors=None):
    """
    For each Bus entrance, ID the trip from GTFS

    O tamanho da tabela inicial pode nao ser
    identico ao da tabela final porque as validacoes sao apagadas
    caso a diferenca entre o momento da validacao e o tempo de saida
    mais proximo do primeiro se verificar superior a 30 minutos
    
    GTFS_SCHEMA = {
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
            "SERVICE" : "service_id"
        },
        "CALENDAR" : {
            "TNAME"   : "calendar_dates",
            "SERVICE" : "service_id",
            "DATE"    : "date"
        }
    }
    
    OTHER_SCHEMA = {
        "ENTRANCES" : {
            "TNAME"    : "val_17jan_7as31",
            "ROUTE"    : ["route_id"],
            "STOP"     : "paragem",
            "TIME"     : "time",
            "CAR"      : "nfrota",
            "DAY"      : "dia",
            "SEQUENCE" : "ordem",
            "CLIENT"   : "ncartao"
        },
        "STOPS" : {
            "TNAME"    : "percursos_geom_v2",
            "ROUTE"    : ["fid_percurso"],
            "SEQUENCE" : "ordem",
            "STOP"     : "paragem"
        }
    }
    
    OTHER_SCHEMA["STOPS"]["ROUTE"] must have the same order than
    OTHER_SCHEMA["ENTRANCES"]["ROUTE"]
    
    Entrances table must have entrances for one GTFS Day 
    (eg: from 04:00:00 to 31:00:00)
    """
    
    import os
    from glass.pys import obj_to_lst
    from glass.sql.db      import create_pgdb
    from glass.it.db import tbl_fromdb_todb
    from glass.sql.col import txt_cols_to_col
    from glass.sql.q import q_to_obj, q_to_ntbl
    from glass.it import db_to_tbl
    
    # Merge ROUTE ID into one column
    OTHER_SCHEMA["STOPS"]["ROUTE"]     = obj_to_lst(
        OTHER_SCHEMA["STOPS"]["ROUTE"])
    OTHER_SCHEMA["ENTRANCES"]["ROUTE"] = obj_to_lst(
        OTHER_SCHEMA["ENTRANCES"]["ROUTE"])
    
    if len(OTHER_SCHEMA["STOPS"]["ROUTE"]) == 1:
        OTHER_SCHEMA["STOPS"]["ROUTE"] = OTHER_SCHEMA["STOPS"]["ROUTE"][0]
    
    else:
        OTHER_SCHEMA["STOPS"]["TNAME"] = txt_cols_to_col(
            conParam, OTHER_SCHEMA["STOPS"]["TNAME"],
            OTHER_SCHEMA["STOPS"]["ROUTE"], "|", "rouid",
            "{}_nr".format(OTHER_SCHEMA["STOPS"]["TNAME"])
        )
        
        OTHER_SCHEMA["STOPS"]["ROUTE"] = "rouid"
    
    if len(OTHER_SCHEMA["ENTRANCES"]["ROUTE"]) == 1:
        OTHER_SCHEMA["ENTRANCES"]["ROUTE"] = OTHER_SCHEMA["ENTRANCES"]["ROUTE"][0]
    
    else:
        OTHER_SCHEMA["ENTRANCES"]["TNAME"] = txt_cols_to_col(
            conParam, OTHER_SCHEMA["ENTRANCES"]["TNAME"],
            OTHER_SCHEMA["ENTRANCES"]["ROUTE"], "", "rouid",
            "{}_nr".format(OTHER_SCHEMA["ENTRANCES"]["TNAME"])
        )
        
        OTHER_SCHEMA["ENTRANCES"]["ROUTE"]
    
    # We have two databases: GTFS AND other with database entrances
    # Send all Relevant data to the same database
    # Create a new one
    newConParam = {
        "HOST" : conGTFS_DB["HOST"], "PORT" : conGTFS_DB["PORT"],
        "USER" : conGTFS_DB["USER"], "PASSWORD" : conGTFS_DB["PASSWORD"]
    }
    create_pgdb(newConParam, newDb, overwrite=True)
    newConParam["DATABASE"] = newDb
    
    # Copy GTFS Tables
    copy_fromdb_todb(conGTFS_DB, newConParam,
        [GTFS_SCHEMA[k]["TNAME"] for k in GTFS_SCHEMA]
    )
    
    # Copy oher db data
    copy_fromdb_todb(conOTHER_DB, newConParam,
        [OTHER_SCHEMA[k]["TNAME"] for k in OTHER_SCHEMA]
    )
    
    # ID circulations and save result in a new table
    service_schema = {
        "TRIPS" : GTFS_SCHEMA["TRIPS"], "CALENDAR" : GTFS_SCHEMA["CALENDAR"],
        "FILTER_DAY" : GTFS_DAY
    }
    
    id_circulations = name_circulations(
        newConParam, GTFS_SCHEMA["STOP_TIMES"], OTHER_SCHEMA["STOPS"],
        "circ_id", serviceSchema=service_schema,
        tripIdColName="fid"
    )
    
    # Sanitize DEPARTURE_TIME FIELD
    update_table(newConParam, GTFS_SCHEMA["STOP_TIMES"]["TNAME"], {
        GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"] : (
            "to_char(TO_TIMESTAMP('{day}' || ' ' || {depTime}, "
            "'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS')"
        ).format(
            day     = ENTRANCES_DAY,
            depTime = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"]
        )
    })
    
    # In stop_times, add meta about the route (add route id)
    q = (
        "SELECT {sT}.{tripId}, {sT}.{stopId}, {sT}.{stopSq}, "
        "{sT}.{depTime}, {idCirc}.{idRoute} FROM {sT} "
        "LEFT JOIN {idCirc} "
        "ON {sT}.{tripId} = {idCirc}.fid "
        "INNER JOIN ("
            "SELECT {tripsTbl}.{tripsTripId}, {calenTbl}.{calenDate} "
            "FROM {tripsTbl} INNER JOIN {calenTbl} ON "
            "{tripsTbl}.{tripsServId} = {calenTbl}.{calenServId}"
        ") AS trip_service "
        "ON {sT}.{tripId} = trip_service.{tripsTripId} "
        "WHERE trip_service.{calenDate} = {day}"
    ).format(
        sT          = GTFS_SCHEMA["STOP_TIMES"]["TNAME"],
        tripId      = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
        stopId      = GTFS_SCHEMA["STOP_TIMES"]["STOP"],
        stopSq      = GTFS_SCHEMA["STOP_TIMES"]["SEQUENCE"],
        depTime     = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        idCirc      = id_circulations,
        idRoute     = OTHER_SCHEMA["STOPS"]["ROUTE"],
        tripsTbl    = GTFS_SCHEMA["TRIPS"]["TNAME"],
        tripsTripId = GTFS_SCHEMA["TRIPS"]["TRIP"],
        tripsServId = GTFS_SCHEMA["TRIPS"]["SERVICE"],
        calenTbl    = GTFS_SCHEMA["CALENDAR"]["TNAME"],
        calenServId = GTFS_SCHEMA["CALENDAR"]["SERVICE"],
        calenDate   = GTFS_SCHEMA["CALENDAR"]["DATE"],
        day         = GTFS_DAY
    )
    
    q_to_ntbl(newConParam, "stop_times_fid", q)
    
    update_table(
        newConParam, "stop_times_fid",
        {OTHER_SCHEMA["STOPS"]["ROUTE"] : "\'notfound\'"},
        {OTHER_SCHEMA["STOPS"]["ROUTE"] : "NULL"        },
        logic_operator='AND'
    )
    
    GTFS_SCHEMA["STOP_TIMES"]["TNAME"] = "stop_times_fid"
    
    # Sanitize time column in entrances table
    q = (
        "SELECT {valRou}, {car}, {stop}, {order}, {card}, "
        "to_char(TO_TIMESTAMP({dayF} || ' ' || {tempo}, "
            "'YYYY-MM-DD HH24:MI:SS'), 'YYYY-MM-DD HH24:MI:SS') AS {tempo} "
        "FROM {tbl}"
    ).format(
        tbl    = OTHER_SCHEMA["ENTRANCES"]["TNAME"],
        valRou = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        car    = OTHER_SCHEMA["ENTRANCES"]["CAR"],
        stop   = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        tempo  = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        dayF   = OTHER_SCHEMA["ENTRANCES"]["DAY"],
        order  = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        card   = OTHER_SCHEMA["ENTRANCES"]["CLIENT"]
    )
    
    OTHER_SCHEMA["ENTRANCES"]["TNAME"] = q_to_ntbl(
        newConParam, f'{OTHER_SCHEMA["ENTRANCES"]["TNAME"]}_san',
        q
    )
    
    # Get a table with the potencial stop_time for one validation
    # For a entrance with IDROUTE 26B|0|ASC will be created a row
    # for each stop_time of the IDROUTE 26B|0|ASC
    Q = (
        "SELECT {valTbl}.{valRou}, {valTbl}.{car}, {valTbl}.{stop}, {valTbl}.{seq}, "
        "{valTbl}.{tempo}, {valTbl}.{card}, {stopTimeTbl}.{tripId}, "
        "{stopTimeTbl}.{stopId}, {stopTimeTbl}.{depTime} "
        "FROM {valTbl} INNER JOIN {stopTimeTbl} "
        "ON {valTbl}.{valRou} = {stopTimeTbl}.{stopsRou} AND "
        "{valTbl}.{stop} = {stopTimeTbl}.{stopId} AND "
        "{valTbl}.{seq} = {stopTimeTbl}.{stopTSeq}"
    ).format(
        valTbl      = OTHER_SCHEMA["ENTRANCES"]["TNAME"],
        valRou      = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        car         = OTHER_SCHEMA["ENTRANCES"]["CAR"],
        stop        = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        tempo       = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        stopTimeTbl = GTFS_SCHEMA["STOP_TIMES"]["TNAME"],
        tripId      = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
        stopId      = GTFS_SCHEMA["STOP_TIMES"]["STOP"],
        depTime     = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        stopsRou    = OTHER_SCHEMA["STOPS"]["ROUTE"],
        seq         = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        card        = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        stopTSeq    = GTFS_SCHEMA["STOP_TIMES"]["SEQUENCE"]
    )
    
    all_poss = q_to_ntbl(
        newConParam, "val_stoptime_all_possibilities", Q
    )
    
    # From the table val_stoptime_all_possibilities
    # Get the correct circulation for each entrance
    timeDifference = (
        "(SELECT *, "
        "("
            "(EXTRACT(day FROM "
                "(TO_TIMESTAMP({timeVal}, 'YYYY-MM-DD HH24:MI:SS') - "
                    "TO_TIMESTAMP({timeDep}, 'YYYY-MM-DD HH24:MI:SS'))"
            ") * 24) + "
            "EXTRACT(hour FROM "
                "(TO_TIMESTAMP({timeVal}, 'YYYY-MM-DD HH24:MI:SS') - "
                    "TO_TIMESTAMP({timeDep}, 'YYYY-MM-DD HH24:MI:SS'))"
            ") + (EXTRACT(minute FROM "
                "(TO_TIMESTAMP({timeVal}, 'YYYY-MM-DD HH24:MI:SS') - "
                    "TO_TIMESTAMP({timeDep}, 'YYYY-MM-DD HH24:MI:SS'))"
            ") / 60.0) + (EXTRACT(second FROM "
                "(TO_TIMESTAMP({timeVal}, 'YYYY-MM-DD HH24:MI:SS') - "
                    "TO_TIMESTAMP({timeDep}, 'YYYY-MM-DD HH24:MI:SS'))"
            ") / 3600.0)"
        ") AS tinterval "
        "FROM {valposs}) AS tmdf"
    ).format(
        timeVal=OTHER_SCHEMA["ENTRANCES"]["TIME"],
        timeDep=GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        valposs=all_poss
    )
    
    q = (
        "SELECT * FROM ("
            "SELECT *, "
            "CASE "
                "WHEN tinterval_abs = MIN(tinterval_abs) OVER (PARTITION BY "
                    "{rouId}, {carId}, {stopId}, {card}, {timeVal}) "
                "THEN 1 ELSE 0 "
            "END AS iscirc "
            "FROM ("
                "SELECT *, ABS(tinterval) AS tinterval_abs "
                "FROM {tmDifT} "
                "WHERE tinterval >= -0.1667 AND tinterval < 0.55"
            ") AS valcirctmp"
        ") AS foo WHERE iscirc = 1"
    ).format(
        rouId   = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        carId   = OTHER_SCHEMA["ENTRANCES"]["CAR"],
        stopId  = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        timeVal = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        card    = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        tmDifT  = timeDifference
    )
    
    val_circ = q_to_ntbl(newConParam, "val_circ", q)
    
    """
    Delete cases when one entrance has more than
    one stop_time with a equal Minimum difference between
    the validation time
    """
    
    q = (
        "SELECT {valcirc}.* "
        "FROM {valcirc} INNER JOIN ("
            "SELECT {rouId}, {stop}, {tempo}, {card}, COUNT({stop}) AS conta "
            "FROM {valcirc} "
            "GROUP BY {rouId}, {stop}, {card}, {tempo}"
        ") AS foo "
        "ON {valcirc}.{rouId} = foo.{rouId} AND {valcirc}.{stop} = foo.{stop} "
        "AND {valcirc}.{tempo} = foo.{tempo} AND {valcirc}.{card} = foo.{card} "
        "WHERE (conta > 1 AND tinterval < tinterval_abs) "
        "OR conta = 1"
    ).format(
        rouId   = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        stop    = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        tempo   = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        card    = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        valcirc = val_circ
    )
    
    val_circ = q_to_ntbl(newConParam, "val_circ_clean", q)
    
    """
    val_circ_clean has many classification errors - wrong circulation
    
    Execute a query to identify these errors
    """
    
    errorQ = (
        "SELECT terrors.*, id_circ.next_circ, id_circ.previous_circ "
        "FROM ("
            "SELECT main.{valRouId}, main.{valStop}, main.{sequence}, "
            "main.{card}, main.{tempo}, "
            "main.{trip}, 1 AS iserror "
            "FROM val_circ_clean AS main INNER JOIN val_circ_clean AS foo "
            "ON main.{trip} = foo.{trip} "
            "WHERE main.{sequence} > foo.{sequence} AND "
            "TO_TIMESTAMP(main.{tempo}, 'YYYY-MM-DD HH24:MI:SS') < "
            "TO_TIMESTAMP(foo.{tempo}, 'YYYY-MM-DD HH24:MI:SS') "
            "GROUP BY main.{valRouId}, main.{valStop}, main.{sequence}, "
            "main.{card}, main.{tempo}, main.{trip}"
        ") AS terrors INNER JOIN ("
            "SELECT *, "
            "LEAD(fid) OVER (PARTITION BY stops, {idRou} ORDER BY departure) "
                "AS next_circ, "
            "LAG(fid) OVER (PARTITION BY stops, {idRou} ORDER BY departure) "
                "AS previous_circ "
            "FROM circ_id"
        ") AS id_circ "
        "ON terrors.{trip} = id_circ.fid"
    ).format(
        valRouId = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        valStop  = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        trip     = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
        idRou    = OTHER_SCHEMA["STOPS"]["ROUTE"],
        card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"]
    )
    
    errors_cls = q_to_ntbl(newConParam, "errors_class", errorQ)
    
    """
    Solve errors - First attempt
    """
    solveQ = (
        "SELECT main.*, errors_class.iserror, "
        "errors_class.next_circ, "
        "errors_class.previous_circ, "
        "CASE "
            "WHEN errors_class.iserror IS NULL THEN main.{tripId} ELSE "
            "errors_class.previous_circ "
        "END AS real_trip "
        "FROM val_circ_clean AS main "
        "LEFT JOIN errors_class "
        "ON main.{rouId} = errors_class.{rouId} "
        "AND main.{stop} = errors_class.{stop} "
        "AND main.{tempo} = errors_class.{tempo} "
        "AND main.{tripId} = errors_class.{tripId} "
        "AND main.{sequence} = errors_class.{sequence} "
        "AND main.{card} = errors_class.{card}"
    ).format(
        rouId    = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        stop     = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        tripId   = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
        sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        depTime  = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"]
    )
    
    error_free = q_to_ntbl(
        newConParam, "val_circ_errorfree1", solveQ)
    
    """
    Identify errors again
    """
    errorQ = (
        "SELECT main.{valRouId}, main.{valStop}, main.{sequence}, "
        "main.{card}, main.{tempo}, "
        "main.real_trip, 1 AS iserror "
        "FROM val_circ_errorfree1 AS main INNER JOIN val_circ_errorfree1 AS foo "
        "ON main.real_trip = foo.real_trip "
        "WHERE main.iserror=1 AND ((main.{sequence} > foo.{sequence} AND "
        "TO_TIMESTAMP(main.{tempo}, 'YYYY-MM-DD HH24:MI:SS') < "
        "TO_TIMESTAMP(foo.{tempo}, 'YYYY-MM-DD HH24:MI:SS')) OR "
        "(main.{sequence} < foo.{sequence} AND "
        "TO_TIMESTAMP(main.{tempo}, 'YYYY-MM-DD HH24:MI:SS') > "
        "TO_TIMESTAMP(foo.{tempo}, 'YYYY-MM-DD HH24:MI:SS'))) "
        "GROUP BY main.{valRouId}, main.{valStop}, main.{sequence}, "
        "main.{card}, main.{tempo}, main.real_trip"
    ).format(
        valRouId = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        valStop  = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        idRou    = OTHER_SCHEMA["STOPS"]["ROUTE"],
        card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"]
    )
    
    q_to_ntbl(newConParam, "errors_class2", errorQ)
    
    solveQ = (
        "SELECT main.*, errors_class2.iserror AS iserror2, "
        "CASE "
            "WHEN errors_class2.iserror IS NULL THEN main.real_trip ELSE "
            "main.next_circ "
        "END AS real_trip2 "
        "FROM val_circ_errorfree1 AS main "
        "LEFT JOIN errors_class2 "
        "ON main.{rouId} = errors_class2.{rouId} "
        "AND main.{stop} = errors_class2.{stop} "
        "AND main.{tempo} = errors_class2.{tempo} "
        "AND main.real_trip = errors_class2.real_trip "
        "AND main.{sequence} = errors_class2.{sequence} "
        "AND main.{card} = errors_class2.{card}"
    ).format(
        rouId    = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        stop     = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        depTime  = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"]
    )
    
    q_to_ntbl(newConParam, "val_circ_errorfree2", solveQ)
    
    if NoErrors:
        """
        Mesmo depois de tudo isto, ha situacoes em que
        se verifica que uma validacao nao pertence nem
        a circulacao seguinte, nem a circulacao anterior.
        Nestes casos, as validacoes sao apagadas pois nao
        e possivel determinar a circulacao.
        """
        
        errorQ = (
            "SELECT main.{valRouId}, main.{valStop}, main.{sequence}, "
            "main.{card}, main.{tempo}, "
            "main.real_trip2, 1 AS iserror3 "
            "FROM val_circ_errorfree2 AS main "
            "INNER JOIN val_circ_errorfree2 AS foo "
            "ON main.real_trip2 = foo.real_trip2 "
            "WHERE main.iserror2=1 AND main.{sequence} > foo.{sequence} AND "
            "TO_TIMESTAMP(main.{tempo}, 'YYYY-MM-DD HH24:MI:SS') < "
            "TO_TIMESTAMP(foo.{tempo}, 'YYYY-MM-DD HH24:MI:SS') "
            "GROUP BY main.{valRouId}, main.{valStop}, main.{sequence}, "
            "main.{card}, main.{tempo}, main.real_trip2"
        ).format(
            valRouId = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
            valStop  = OTHER_SCHEMA["ENTRANCES"]["STOP"],
            sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
            tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
            idRou    = OTHER_SCHEMA["STOPS"]["ROUTE"],
            card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"]
        )
        
        q_to_ntbl(newConParam, "errors_class3", errorQ)
        
        solveQ = (
            "SELECT main.*, errors_class3.iserror3, "
            "CASE "
                "WHEN errors_class3.iserror3 = 1 THEN 'not_found' "
                "ELSE main.real_trip2 "
            "END AS real_trip3 "
            "FROM val_circ_errorfree2 AS main "
            "LEFT JOIN errors_class3 "
            "ON main.{rouId} = errors_class3.{rouId} "
            "AND main.{stop} = errors_class3.{stop} "
            "AND main.{tempo} = errors_class3.{tempo} "
            "AND main.real_trip2 = errors_class3.real_trip2 "
            "AND main.{sequence} = errors_class3.{sequence} "
            "AND main.{card} = errors_class3.{card}"
        ).format(
            rouId    = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
            stop     = OTHER_SCHEMA["ENTRANCES"]["STOP"],
            tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
            tripId   = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
            sequence = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
            card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
            depTime  = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"]
        )
        
        q_to_ntbl(newConParam, "val_circ_errorfree3", solveQ)
        
        realTrip  = "real_trip3"
        errorfree = "val_circ_errorfree3"
    
    else:
        realTrip  = "real_trip2"
        errorfree = "val_circ_errorfree2"
    
    """
    TODO: Use nfrota to identify errors
    """
    
    # Produce final table
    if os.path.splitext(OutTable)[1] == '':
        outpg = OutTable
    
    else:
        outpg = os.path.splitext(os.path.basename(OutTable))[0]
    
    finalQ = (
        "SELECT main.{route}, main.{car}, main.{card}, "
        "main.{stop}, main.{order}, main.{tempo}, "
        "main.{realtrip} AS {tripId}, "
        "circ_id.departure AS departure_circ, circ_id.depar_last_stop, "
        "foo.{stopTime} AS departure_stop "
        "FROM {tblerrorfree} AS main "
        "INNER JOIN circ_id "
        "ON main.{realtrip} = circ_id.fid "
        "INNER JOIN {stopTbl} AS foo "
        "ON main.{realtrip} = foo.{tripId} AND "
        "main.{stop} = foo.{stopId} AND main.{order} = "
        "foo.{sequence}"
    ).format(
        route    = OTHER_SCHEMA["ENTRANCES"]["ROUTE"],
        car      = OTHER_SCHEMA["ENTRANCES"]["CAR"],
        card     = OTHER_SCHEMA["ENTRANCES"]["CLIENT"],
        stop     = OTHER_SCHEMA["ENTRANCES"]["STOP"],
        order    = OTHER_SCHEMA["ENTRANCES"]["SEQUENCE"],
        tempo    = OTHER_SCHEMA["ENTRANCES"]["TIME"],
        tripId   = GTFS_SCHEMA["STOP_TIMES"]["TRIP"],
        stopTbl  = GTFS_SCHEMA["STOP_TIMES"]["TNAME"],
        stopTime = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        stopId   = GTFS_SCHEMA["STOP_TIMES"]["STOP"],
        sequence = GTFS_SCHEMA["STOP_TIMES"]["SEQUENCE"],
        realtrip=realTrip, tblerrorfree=errorfree
    )
    
    q_to_ntbl(newConParam, outpg, finalQ)
    
    if os.path.splitext(OutTable)[1] == '.xlsx':
        db_to_tbl(outpg, OutTable, outpg, newConParam)
    
    return OutTable

