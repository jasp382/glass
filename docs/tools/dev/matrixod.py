"""
Generate MATRIX OD FROM ENTRANCES INSTANCES IN PGTABLE
"""


def trip_chain_meth(conParam, TABLES_SCHEMA, output, FILTER_DAY=None,
                    FILTER_TIME=None, saveTempTables=None):
    """
    Returns a OD Matrix using the origins registered in one PGTABLE
    
    Apply Trip-Chaining Method
    
    Sample TABLES_SCHEMA:
    TABLES_SCHEMA = {
        "VALIDATIONS" : {
            "TNAME"  : "id_pares_od",
            "DAY"    : "dia",
            "TIME"   : "time",
            "HOUR"   : "hora",
            "MINUTE" : "minuto",
            "SECOND" : "segundo",
            "ROUTE"  : "fid_percurso",
            "STOP"   : "paragem",
            "CLIENT" : "ncartao"
        },
        "ISOCHRONES" : {
            "TNAME"  : "isocronas",
            "STOP"   : "id",
            "GEOM"   : "geom"
    },
        "STOPS" : {
            "TNAME" : "percursos_geom_v2",
            "ROUTE" : "fid_percurso",
            "STOP"  : "paragem",
            "GEOM"  : "geom"
        }
    }
    
    FILTER_DAY = [
        '2018-01-08', '2018-01-09', '2018-01-10', '2018-01-11',
        '2018-01-12', '2018-01-15', '2018-01-16', '2018-01-17',
        '2018-01-18', '2018-01-19', '2018-01-22', '2018-01-23',
        '2018-01-24', '2018-01-25', '2018-01-26', '2018-01-29',
        '2018-01-30', '2018-01-31'
    ]
    
    FILTER_TIME = ["09:00:00", "10:00:00"]
    """
    
    from glass.pys                 import obj_to_lst
    from glass.cpu.psql.mng.fld    import drop_column
    from glass.sql.q     import q_to_ntbl
    from glass.sql.tbl import replace_null_with_other_col_value
    from glass.cpu.psql.mng._del   import drop_where_cols_are_same
    from glass.cpu.psql.mng._del   import del_tables
    from glass.cpu.psql.anls.count import sel_where_groupByIs
    from glass.mob.bustops         import get_isValidDestination_table
    from glass.mob.bustops         import get_nearStopTable
    from glass.to.xls              import psql_to_xls
    
    # List to record generated tables
    LONG_TABLES = []
    
    # From BUS entrances, erase cases where there is only one validation
    # per day and card
    FILTER_DAY = obj_to_lst(FILTER_DAY)
    if FILTER_DAY:
        whereStr = " OR ".join(
            "{}.{}='{}'".format(
                TABLES_SCHEMA["VALIDATIONS"]["TNAME"],
                TABLES_SCHEMA["VALIDATIONS"]["DAY"], x
            ) for x in FILTER_DAY
        )
    
    else:
        whereStr = None
       
    tabledata = sel_where_groupByIs(
        conParam, TABLES_SCHEMA["VALIDATIONS"]["TNAME"],
        [TABLES_SCHEMA["VALIDATIONS"]["CLIENT"], TABLES_SCHEMA["VALIDATIONS"]["DAY"]],
        ">", "1", "p_{}".format(TABLES_SCHEMA["VALIDATIONS"]["TNAME"]),
        filterWhere=whereStr
    )
    
    LONG_TABLES.append(tabledata)
    
    # Assign destinations to origins
    QUERY = (
        "SELECT *, "
        "first_value({routeF}) OVER(PARTITION BY {cardF}, {dayF} "
            "ORDER BY {dayF}, {hourF}, {minF}, {secF}) AS tmpv, "
        "first_value({stopF}) OVER(PARTITION BY {cardF}, {dayF} "
            "ORDER BY {dayF}, {hourF}, {minF}, {secF}) AS tmpst "
        "FROM ("
            "SELECT *, "
            "row_number() OVER(PARTITION BY {cardF}, {dayF} "
                "ORDER BY {cardF}, {dayF}, {hourF}, {minF}, {secF}) AS valorder, "
            "lead({routeF}) OVER(PARTITION BY {cardF}, {dayF} "
                "ORDER BY {cardF}, {dayF}, {hourF}, {minF}, {secF}) AS dest_route, "
            "lead({stopF}) OVER(PARTITION BY {cardF}, {dayF} "
                "ORDER BY {cardF}, {dayF}, {hourF}, {minF}, {secF}) AS dest_stop "
            "FROM {t} ORDER BY {cardF}, {dayF}, {hourF}, {minF}, {secF}"
        ") AS sub_tbl"
    ).format(
        dayF   = TABLES_SCHEMA["VALIDATIONS"]["DAY"],
        hourF  = TABLES_SCHEMA["VALIDATIONS"]["HOUR"],
        minF   = TABLES_SCHEMA["VALIDATIONS"]["MINUTE"],
        secF   = TABLES_SCHEMA["VALIDATIONS"]["SECOND"],
        t      = tabledata,
        stopF  = TABLES_SCHEMA["VALIDATIONS"]["STOP"],
        cardF  = TABLES_SCHEMA["VALIDATIONS"]["CLIENT"],
        routeF = TABLES_SCHEMA["VALIDATIONS"]["ROUTE"]
    )
    
    q_to_ntbl(conParam, "p_matrix_od", QUERY)
    
    LONG_TABLES.append("p_matrix_od")
    
    # Update null values
    # Last validation of the day does not have destiny
    # This will be the first validation of the day
    replace_null_with_other_col_value(
        conParam, "p_matrix_od", 'dest_route', 'tmpv'
    )
    
    replace_null_with_other_col_value(
        conParam, "p_matrix_od", 'dest_stop', 'tmpst'
    )
    
    drop_column(conParam, "p_matrix_od", ["tmpv", "tmpst"])
    
    # It is possible to find rows in which
    # origins and destinations are the same
    # Delete rows where this happens
    drop_where_cols_are_same(
        conParam, "p_matrix_od",
        TABLES_SCHEMA["VALIDATIONS"]["STOP"],
        "dest_stop"
    )
    
    # Compacting table: GROUP BY origin && destination
    if FILTER_TIME:
        whereTime = (
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') >= "
            "TO_TIMESTAMP('{timeLower}', 'HH24:MI:SS') AND "
            "TO_TIMESTAMP({timeCol}, 'HH24:MI:SS') < "
            "TO_TIMESTAMP('{timeUpper}', 'HH24:MI:SS')"
        ).format(
            timeCol   = TABLES_SCHEMA["VALIDATIONS"]["TIME"],
            timeLower = FILTER_TIME[0],
            timeUpper = FILTER_TIME[1]
        )
    
    else:
        whereTime = None
    
    compact_Query = (
        "SELECT {routeF}, {stopF}, dest_stop, COUNT({routeF}) AS trip_count "
        "FROM p_matrix_od {whr}"
        "GROUP BY {routeF}, {stopF}, dest_stop"
    ).format(
        routeF = TABLES_SCHEMA["VALIDATIONS"]["ROUTE"],
        stopF  = TABLES_SCHEMA["VALIDATIONS"]["STOP"],
        whr    = "" if not whereTime else "WHERE {} ".format(whereTime)
    )
    
    q_to_ntbl(conParam, "p_matrix_od_gp", compact_Query)
    
    LONG_TABLES.append("p_matrix_od_gp")
    
    """
    See if destinations are valid.
    See if second validation could be a destination of the first validation
    """
    
    # For that we need to know which isochrones intersects a specific points
    # Create a table AS (stop_a_route | stop_b | bool_intersect)
    # In the future it will be possible to relate p_matrix_od with this new
    # table and know if the destination is possible.
    destIsValidTbl = get_isValidDestination_table(
        conParam, TABLES_SCHEMA["STOPS"]["TNAME"],
        TABLES_SCHEMA["STOPS"]["STOP"],
        TABLES_SCHEMA["STOPS"]["GEOM"],
        TABLES_SCHEMA["STOPS"]["ROUTE"],
        TABLES_SCHEMA["ISOCHRONES"]["TNAME"],
        TABLES_SCHEMA["ISOCHRONES"]["STOP"],
        TABLES_SCHEMA["ISOCHRONES"]["GEOM"],
        'p_int_valtable'
    )
    
    LONG_TABLES.append("p_int_valtable")
    
    q_to_ntbl(conParam, "p_matrix_od_valid", (
        "SELECT p_matrix_od_gp.*, {isDestValidT}.bintersect "
        "FROM p_matrix_od_gp INNER JOIN {isDestValidT} "
        "ON p_matrix_od_gp.{routeF} = {isDestValidT}.{stoRouteF} AND "
        "p_matrix_od_gp.dest_stop = {isDestValidT}.stop_b "
        "WHERE bintersect = 1"
    ).format(
        routeF       = TABLES_SCHEMA["VALIDATIONS"]["ROUTE"],
        stoRouteF    = TABLES_SCHEMA["STOPS"]["ROUTE"],
        isDestValidT = destIsValidTbl
    ))
    
    LONG_TABLES.append("p_matrix_od_valid")
    
    # Find real destinations
    # 1 Creates a table with the distance between all stops and the near
    # stop of another route
    nearStopTable = get_nearStopTable(conParam,
        TABLES_SCHEMA["STOPS"]["TNAME"], TABLES_SCHEMA["STOPS"]["STOP"],
        TABLES_SCHEMA["STOPS"]["GEOM"], TABLES_SCHEMA["STOPS"]["ROUTE"],
        "p_near_stops"
    )
    
    LONG_TABLES.append(nearStopTable)
    
    # 2 Query to find real destinations
    QrealDest = (
        "SELECT p_matrix_od_valid.{validRoute} AS origin_route, "
        "p_matrix_od_valid.{validStop} AS origin_stop, "
        "p_matrix_od_valid.dest_stop AS next_origin, "
        "{nearStops}.stop_a AS destination_stop, "
        "trip_count AS trips_number "
        "FROM p_matrix_od_valid "
        "INNER JOIN {nearStops} ON "
        "p_matrix_od_valid.{validRoute} = {nearStops}.{stopsRoute} AND "
        "p_matrix_od_valid.dest_stop = {nearStops}.stop_b"
    ).format(
        nearStops  = nearStopTable,
        validRoute = TABLES_SCHEMA["VALIDATIONS"]["ROUTE"],
        stopsRoute = TABLES_SCHEMA["STOPS"]["ROUTE"],
        validStop  = TABLES_SCHEMA["VALIDATIONS"]["STOP"]
    )
    
    q_to_ntbl(conParam, "p_matrix_od_final", QrealDest)
    
    LONG_TABLES.append("p_matrix_od_final")
    
    # Get a version of the final table only with origin and next origin
    q_to_ntbl(conParam, "p_matrix_od_pseudo_dest", (
        "SELECT origin_stop, next_origin, "
        "SUM(trips_number) AS trips_number "
        "FROM p_matrix_od_final "
        "GROUP BY origin_stop, next_origin"
    ))
    
    LONG_TABLES.append("p_matrix_od_pseudo_dest")
    
    # Get a version of the final table only with origin and the destination
    # in the same route
    q_to_ntbl(conParam, "p_matrix_od_real_dest", (
        "SELECT origin_stop, destination_stop, "
        "SUM(trips_number) AS trips_number "
        "FROM p_matrix_od_final "
        "GROUP BY origin_stop, destination_stop"
    ))
    
    LONG_TABLES.append("p_matrix_od_real_dest")
    
    # Export table to Excel
    expTbl = [
        "p_matrix_od_final", "p_matrix_od_pseudo_dest",
        "p_matrix_od_real_dest"
    ]
    psql_to_xls(expTbl, output, expTbl, conParam)
    
    if not saveTempTables:
        del_tables(conParam, LONG_TABLES)
    
    return output
 
    