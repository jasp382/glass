"""
Tools to measure Time Distances using GTFS Data
"""

def timedist_stopsPairs(db, GTFS_SCHEMA, outfile):
    """
    Use GTFS DB to calculate the mean time between all stops pairs for all
    route_id.
    
    Definition of a stop pair:
    For a route with 10 stops, the time distance will be estimated
    for the following pairs: 1|2; 2|3; 3|4; 4|5; 5|6; 6|7; 7|8; 8|9; 9|10.
    So, the time distance will not be calculated for all possible combinations
    of bus stops.
    
    GTFS_SCHEMA = {
        "TRIPS" : {
            "TNAME"    : "trips",
            "TRIP_ID"  : "trip_id",
            "ROUTE_ID" : "route_id"
        },
        "ROUTES" : {
            "TNAME"      : "routes",
            "ROUTE_ID"   : "route_id",
            "ROUTE_NAME" : "route_short_name"
        },
        "STOP_TIMES" : {
            "TNAME"     : "stop_times",
            "TRIP_ID"   : "trip_id",
            "STOP_ID"   : "stop_id",
            "ORDER"     : "stop_sequence",
            "ARRIVAL"   : "arrival_time",
            "DEPARTURE" : "departure_time"
        }
    }
    
    The output will be something like this:
    route | origin | o_order | destination | d_order | duration
     12E  |  XXX   |    1    |    XXX      |    2    | XX:XX:XX
     12E  |  XXX   |    2    |    XXX      |    3    | XX:XX:XX
     12E  |  XXX   |    3    |    XXX      |    4    | XX:XX:XX
     12E  |  XXX   |    4    |    XXX      |    5    | XX:XX:XX
     12E  |  XXX   |    5    |    XXX      |    6    | XX:XX:XX
     12E  |  XXX   |    6    |    XXX      |    7    | XX:XX:XX
     15E  |  XXX   |    1    |    XXX      |    2    | XX:XX:XX
     15E  |  XXX   |    2    |    XXX      |    3    | XX:XX:XX
     15E  |  XXX   |    3    |    XXX      |    4    | XX:XX:XX
     15E  |  XXX   |    4    |    XXX      |    5    | XX:XX:XX
    """
    
    from glass.ng.sql.q import q_to_obj
    from glass.ng.wt    import obj_to_tbl
    
    SQL_QUERY = (
        "SELECT route, origin, o_order, destination, d_order, AVG(duration) AS duration FROM ("
            "SELECT foo.*, (foo.time_arrival - foo.time_departure) AS duration FROM ("
                "SELECT {tripid}, {stopid} AS origin, {stp_order} AS o_order, "
                "LEAD({stopid}) OVER(PARTITION BY {tripid} ORDER BY {tripid}, {stp_order}) AS destination, "
                "LEAD({stp_order}) OVER(PARTITION BY {tripid} ORDER BY {tripid}, {stp_order}) AS d_order, "
                "TO_TIMESTAMP({dep_time}, 'HH24:MI:SS') AS time_departure, "
                "LEAD(TO_TIMESTAMP({arr_time}, 'HH24:MI:SS')) OVER("
                    "PARTITION BY {tripid} ORDER BY {tripid}, {stp_order}) AS time_arrival, "
                "{route_name} AS route FROM {stopTm} INNER JOIN ("
                    "SELECT {tripsT}.{Ttripsid} AS trip_fid, "
                    "{routesT}.{route_name} FROM {tripsT} INNER JOIN {routesT} ON "
                    "{tripsT}.{Ttrouteid} = {routesT}.{Rrouteid}"
                ") AS trips_routes ON {stopTm}.{tripid} = trips_routes.trip_fid "
                "ORDER BY {tripid}, {stp_order}"
            ") AS foo "
            "WHERE time_arrival IS NOT NULL "
            "ORDER BY {tripid}, o_order"
        ") AS allods "
        "GROUP BY route, origin, o_order, destination, d_order "
        "ORDER BY route, o_order"
    ).format(
        tripid     = GTFS_SCHEMA["STOP_TIMES"]["TRIP_ID"],
        stopid     = GTFS_SCHEMA["STOP_TIMES"]["STOP_ID"],
        stp_order  = GTFS_SCHEMA["STOP_TIMES"]["ORDER"],
        dep_time   = GTFS_SCHEMA["STOP_TIMES"]["DEPARTURE"],
        arr_time   = GTFS_SCHEMA["STOP_TIMES"]["ARRIVAL"],
        stopTm     = GTFS_SCHEMA["STOP_TIMES"]["TNAME"],
        route_name = GTFS_SCHEMA["ROUTES"]["ROUTE_NAME"],
        routesT    = GTFS_SCHEMA["ROUTES"]["TNAME"],
        Rrouteid   = GTFS_SCHEMA["ROUTES"]["ROUTE_ID"],
        Ttrouteid  = GTFS_SCHEMA["TRIPS"]["ROUTE_ID"],
        tripsT     = GTFS_SCHEMA["TRIPS"]["TNAME"],
        Ttripsid   = GTFS_SCHEMA["TRIPS"]["TRIP_ID"]
    )
    
    table = q_to_obj(db, SQL_QUERY)
    
    return obj_to_tbl(table, outfile)

