"""
Methods related with BUS Stops
"""

def get_isValidDestination_table(db, stopsTable, stopsId, stopsGeom, stopsRoute,
                                 isochronesTable, isoStop, isoGeom, outTable):
    """
    Create a table that shows if a certain BUS Stop is a valid
    destination for the BUS Stops of a certain route.
    
    OUTPUT TABLE SCHEMA:
    (stop_a_route | stop_b | isValid)
    
    stop_b is a valid destination for any stop of the stop_a_route
    if an isochrone (10 min) from stop_b intersects with any stop of the
    stop_a_route.
    """
    
    from glass.sql.q import q_to_ntbl
    
    q = (
        "SELECT {routeF}, stop_b, "
        "MAX(CASE WHEN bool_intersect IS true THEN 1 ELSE 0 END) AS bintersect "
        "FROM ("
            "SELECT stops1.{routeF}, stops1.{stopF} AS stop_a, "
            "stops1.stop_geom AS stop_geom, "
            "stops2.{stopF} AS stop_b, stops2.iso_geom AS iso_geom, "
            "ST_Intersects(stops1.stop_geom, stops2.iso_geom) AS bool_intersect "
            "FROM ("
                "SELECT {routeF}, {stopF}, {stopG} AS stop_geom FROM {t} "
                "GROUP BY {routeF}, {stopF}, {stopG}"
            ") AS stops1, ("
                "SELECT stops.{stopF}, {isoT}.{isoG} AS iso_geom FROM ("
                    "SELECT {stopF}, {stopG} FROM {t} GROUP BY {stopF}, {stopG}"
                ") AS stops INNER JOIN {isoT} ON stops.{stopF} = {isoT}.{isoID}"
            ") AS stops2"
        ") AS foo GROUP BY {routeF}, stop_b"
    ).format(
        routeF=stopsRoute, stopF=stopsId, stopG=stopsGeom,
        isoT=isochronesTable, isoG=isoGeom, t=stopsTable,
        isoID=isoStop
    )
    
    q_to_ntbl(db, outTable, q)
    
    return outTable


def get_nearStopTable(db, stopsTable, stopsId, stopsGeom, stopsRoute, outT):
    """
    Creates a table with the distance between all stops and the near
    stop of another route
    """
    
    from glass.sql.q import q_to_ntbl
    
    q = (
        "SELECT * FROM ("
            "SELECT {routeF}, stop_b, "
            "CASE WHEN distance = MIN(distance) OVER("
                "PARTITION BY {routeF}, stop_b) "
                "THEN stop_a ELSE NULL END AS stop_a, "
            "CASE WHEN distance = MIN(distance) OVER("
                "PARTITION BY {routeF}, stop_b) "
                "THEN distance ELSE NULL END AS distance "
            "FROM ("
                "SELECT {routeF}, stop_a, stop_a_geom, stop_b, stop_b_geom, "
                "ST_Distance(stop_a_geom, stop_b_geom) AS distance "
                "FROM ("
                    "SELECT {routeF}, {stopF} AS stop_a, {stopG} AS stop_a_geom "
                    "FROM {t} GROUP BY {routeF}, {stopF}, {stopG}"
                ") AS stops1, ("
                    "SELECT {stopF} AS stop_b, {stopG} AS stop_b_geom "
                    "FROM {t} GROUP BY {stopF}, {stopG}"
                ") AS stops2"
            ") AS foo"
        ") AS foo2 "
        "WHERE stop_a IS NOT NULL"
    ).format(
        routeF=stopsRoute, t=stopsTable, stopF=stopsId, stopG=stopsGeom
    )
    
    q_to_ntbl(db, outT, q)
    
    return outT

