"""
Time distance tools
"""


def cumulated_timedist_bet_stops(db, STOPS_BY_ROUTE_TABLE,
                                 STOP_TIMES_TABLE, OUT_TABLE):
    """
    Calculate the time distance between all possible paths in a bus travel
    network.
    
    Imagine a table with all Stops for several routes
       | route | stop | order
     0 |  15E  | 15E1 |   1
     1 |  15E  | 15E2 |   2
     2 |  15E  | 15E3 |   3
     3 |  15E  | 15E4 |   4
     4 |  15E  | 15E5 |   5
     5 |  12E  | 12E1 |   1
     6 |  12E  | 12E2 |   2
     7 |  12E  | 12E3 |   3
     8 |  12E  | 12E4 |   4
     9 |  12E  | 12E5 |   5
    
    And other table with the timedelta between stops of a route
    considering stops order (timedelta by order - 1|2; 2|3; 3|4...)
    ENTITY | ORIGIN | DESTINATION | DURATION
      12E  |  12E1  |    12E2     | 00:02:30
      12E  |  12E2  |    12E3     | 00:02:15
      12E  |  12E3  |    12E4     | 00:01:18
      12E  |  12E4  |    12E5     | 00:03:06
      15E  |  15E1  |    15E2     | 00:04:56
      15E  |  15E2  |    15E3     | 00:02:51
      15E  |  15E3  |    15E4     | 00:02:30
      15E  |  15E4  |    15E5     | 00:01:12
    
    This method will use the presented tables to create a new table as:
    The new table will have the time interval for all trips possible in
    one route.
       | route | stop_a | order_a | stop_b | order_b | timedelta
     0 |  15E  |  15E1  |    1    |  15E2  |    2    |    xxx
     1 |  15E  |  15E1  |    1    |  15E3  |    3    |    xxx
     2 |  15E  |  15E1  |    1    |  15E4  |    4    |    xxx
     3 |  15E  |  15E1  |    1    |  15E5  |    5    |    xxx
     4 |  15E  |  15E2  |    2    |  15E3  |    3    |    xxx
     5 |  15E  |  15E2  |    2    |  15E4  |    4    |    xxx
     6 |  15E  |  15E2  |    2    |  15E5  |    5    |    xxx
     7 |  15E  |  15E3  |    3    |  15E4  |    4    |    xxx
     8 |  15E  |  15E3  |    3    |  15E5  |    5    |    xxx
     ...
     9 |  12E  |  12E1  |    1    |  12E2  |    2    |    xxx
    10 |  12E  |  12E1  |    1    |  12E3  |    3    |    xxx
    11 |  12E  |  12E1  |    1    |  12E4  |    4    |    xxx
    12 |  12E  |  12E1  |    1    |  12E5  |    5    |    xxx
    13 |  12E  |  12E2  |    2    |  12E3  |    3    |    xxx
    14 |  12E  |  12E2  |    2    |  12E4  |    4    |    xxx
    15 |  12E  |  12E2  |    2    |  12E5  |    5    |    xxx
    ...
    
    Inputs samples:
    STOPS_BY_ROUTE_TABLE = {"NAME" : "percursos_geom_v2",
        "ID" : "fid_percurso", "STOP" : "paragem", "ORDER" : "ordem",
        "CIRC" : "sentido", "ISCIRC" : "'CIRC'"
    }
    
    STOP_TIMES_TABLE = {
        "FILE"   : r"/path/to/mean_time_pairs_od.xlsx",
        "ROUTE"  : "route",
        "ORIGIN" : "origin",
        "DESTIN" : "destination",
        "TIME_F" : "time_duration"
    }
    """
    
    import pandas
    from glass.tbl.xls.fm  import xlstimedelta_to_pddf
    from glass.sql.q   import q_to_obj, q_to_ntbl
    from glass.sql.c   import alchemy_engine
    from glass.sql.tbl import tbls_to_tbl
    from glass.sql.tbl import del_tables
    
    def get_stops_by_route(isCIRC):
        stp_by_route = q_to_obj(db, (
            "SELECT {t}.{routeF} AS fid_route, {t}.{stopF} AS stop_a, "
            "{t}.{orderF} AS order_a, "
            "aux.{stopF} AS stop_b, aux.{orderF} AS order_b "
            "FROM {t} INNER JOIN {t} AS aux "
            "ON {t}.{routeF} = aux.{routeF} "
            "WHERE {t}.{circfield}{operator}{circvalue} "
            "ORDER BY {t}.{routeF}, {t}.{orderF}, aux.{orderF}"
        ).format(
            routeF    = STOPS_BY_ROUTE_TABLE["ID"],
            stopF     = STOPS_BY_ROUTE_TABLE["STOP"],
            orderF    = STOPS_BY_ROUTE_TABLE["ORDER"],
            t         = STOPS_BY_ROUTE_TABLE["NAME"],
            circfield = STOPS_BY_ROUTE_TABLE["CIRC"],
            circvalue = STOPS_BY_ROUTE_TABLE["ISCIRC"],
            operator  = "=" if isCIRC else "<>"
        ))
        
        return stp_by_route
    
    # Get time for each ordered pair of stops in a route
    # (not all possible pairs/trips)
    time_by_routes = xlstimedelta_to_pddf(
        STOP_TIMES_TABLE["FILE"], STOP_TIMES_TABLE["TIME_F"],
        columnsToMantain=[
            STOP_TIMES_TABLE["ROUTE"], STOP_TIMES_TABLE["ORIGIN"],
            STOP_TIMES_TABLE["DESTIN"], STOP_TIMES_TABLE["TIME_F"]
        ]
    )
    
    def assign_duration_to_trips(table):
        """
        Assign time travel between origin and destination
        in a new column of the table object
        """
        
        # Create auxiliar table for self join
        aux_join = table.copy()
        
        # Rename cols of aux_join
        aux_join.rename(columns={
            "fid_route" : "fid_aux", "stop_a": "aux_a", "stop_b": "aux_b",
            "order_a" : "aux_o_a", "order_b" : "aux_o_b"
        }, inplace=True)
        
        # Execute Join
        joined = table.merge(aux_join, how='inner',
                             left_on="fid_route", right_on="fid_aux")
        
        joined.drop("fid_aux", axis=1, inplace=True)
        
        joined = joined[
            (joined["order_b"] >= joined["aux_o_b"]) & \
            (joined["order_a"] <= joined["aux_o_a"]) & \
            (joined["aux_o_b"] - joined["aux_o_a"] == 1)
        ]
        
        # aaa is route
        #joined["aaa"] = joined["fid_route"].str[:3]
        joined["aaa"] = joined.fid_route
        
        table_with_duration = joined.merge(
            time_by_routes, how='inner',
            left_on=["aaa", "aux_a", "aux_b"],
            right_on=[STOP_TIMES_TABLE["ROUTE"], STOP_TIMES_TABLE["ORIGIN"],
                      STOP_TIMES_TABLE["DESTIN"]]
        )
        
        table_with_duration.drop([
            "aux_a", "aux_o_a", "aux_b", "aux_o_b",
            "aaa", STOP_TIMES_TABLE["ROUTE"], STOP_TIMES_TABLE["ORIGIN"],
            STOP_TIMES_TABLE["DESTIN"]
        ], axis=1, inplace=True)
        
        table_with_duration[STOP_TIMES_TABLE["TIME_F"]] = table_with_duration.groupby(
            ["fid_route", "stop_a", "order_a", "stop_b", "order_b"]
        )[STOP_TIMES_TABLE["TIME_F"]].transform('sum')
        
        table_with_duration[
            STOP_TIMES_TABLE["TIME_F"]] = table_with_duration[
                STOP_TIMES_TABLE["TIME_F"]].astype(str)
        
        grpby = table_with_duration.drop_duplicates(inplace=False)
        
        return grpby
    
    """
    Get all possible stops pairs - Excluding CIRCULAR ROUTES
    """
    stops_by_route = get_stops_by_route(None)
    
    # Remove WHERE order_a is equal or greater than order_b (invalid trips)
    stops_by_route = stops_by_route[
        stops_by_route["order_a"] < stops_by_route["order_b"]
    ]
    
    # Assign duration of the travel between the stop pairs in each row
    __routes = stops_by_route["fid_route"].unique()
    
    tables_by_route = []
    for r in __routes:
        selStopsByRoute = stops_by_route[stops_by_route["fid_route"] == r]
        new_table = assign_duration_to_trips(selStopsByRoute)
        
        tables_by_route.append(new_table)
    
    """
    Get all possible stops pairs - Only CIRCULAR ROUTES
    """
    stops_by_route_circ = get_stops_by_route(True)
    
    # Remove WHERE order_a is equal to order_b (invalid trips for circular routes)
    # Add a second turn to stops_by_route_circ
    second_circ = stops_by_route_circ.copy()
    second_circ["max"] = second_circ.groupby(
        ["fid_route"])["order_b"].transform('max')
    
    second_circ["order_a"] = second_circ["order_a"] + second_circ["max"]
    second_circ["order_b"] = second_circ["order_b"] + second_circ["max"]
    second_circ.drop("max", axis=1, inplace=True)
    
    third_circ = stops_by_route_circ.copy()
    third_circ["max"] = third_circ.groupby(
        ["fid_route"])["order_b"].transform("max")
    third_circ["order_b"] = third_circ["order_b"] + third_circ["max"]
    third_circ.drop("max", axis=1, inplace=True)
    
    stops_by_route_circ = stops_by_route_circ.append(
        [second_circ, third_circ], ignore_index=True
    )
    
    stops_by_route_circ = stops_by_route_circ[
        stops_by_route_circ["order_a"] < stops_by_route_circ["order_b"]
    ]
    
    __routes = stops_by_route_circ["fid_route"].unique()
    for r in __routes:
        selStopsByRoute = stops_by_route_circ[
            stops_by_route_circ["fid_route"] == r]
        
        new_table = assign_duration_to_trips(selStopsByRoute)
        tables_by_route.append(new_table)
    
    # Send data to PostgreSQL
    engine = alchemy_engine(db)
    
    ltables = []
    for i in range(len(tables_by_route)):
        # Get dataframe shape
        nrows = int(tables_by_route[i].shape[0])
        if not nrows:
            continue
        
        tables_by_route[i].to_sql(
            "{}_{}".format(OUT_TABLE, str(i)), engine, chunksize=10000
        )
        ltables.append("{}_{}".format(OUT_TABLE, str(i)))
    
    tbls_to_tbl(db, ltables, OUT_TABLE + "_notime")
    
    q_to_ntbl(db, OUT_TABLE, (
        "SELECT fid_route, stop_a, order_a, stop_b, order_b, "
        "CAST(split_part(REPLACE({td}, '0 days ', ''), '.', 1) AS Interval) "
        "AS {td} FROM {t}").format(
            td=STOP_TIMES_TABLE["TIME_F"], t=OUT_TABLE + "_notime"
        )
    )
    
    ltables.append(OUT_TABLE + "_notime")
    
    del_tables(db, ltables)
    
    return OUT_TABLE

