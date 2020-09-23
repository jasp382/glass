"""
OpenTripPlanner
"""

def clsfacility(i, f, hd, d, out_epsg=None):
    """
    Closest Facility using OTP
    i - incidents
    f = facilities
    hd = hourday
    d = date

    i and f must have geometry column
    """

    import requests
    import polyline
    import pandas as pd
    from shapely.geometry  import LineString
    from shapely.ops       import linemerge
    from geopandas         import GeoDataFrame
    from glass.geo.obj.prj import df_prj
    from glass.cons.otp    import PLANNER_URL

    #TODO: i and f must be pandas dataframes

    error_logs = []
    # Results
    # incident_id, facility_id, minutes, walkmin, tranmin, waitmin, geom
    results = []

    for idx, r in i.iterrows():
        duration    = None
        plan_record = None

        for e, _r in f.iterrows():
            fromPlace = str(r.geometry.y) + ',' + str(r.geometry.x)
            toPlace   = str(_r.geometry.y) + ',' + str(_r.geometry.x)

            resp = requests.get(PLANNER_URL, params={
                'fromPlace'       : fromPlace,
                'toPlace'         : toPlace,
                'time'            : hd,
                'date'            : d,
                'mode'            : 'TRANSIT,WALK',
                'maxWalkDistance' : 50000,
                'arriveBy'        : 'false',
                'numItineraries'  : 1
            }, headers={'accept'  : 'application/json'})

            # Get Response JSON
            data = resp.json()

            if "error" in data:
                error_logs.append([idx, e, data["error"]])
                continue

            # Get Iteneraries
            it = data['plan']["itineraries"][0]

            if not duration or duration > it["duration"]:
                duration = it["duration"]

                # Get intenerary geometry
                geoms = [LineString(polyline.decode(p["legGeometry"]["points"], geojson=True)) for p in it['legs']]
                
                geom = linemerge(geoms)

                plan_record = [
                    idx, e, it["duration"] / 60, it["walkTime"] / 60,
                    it["transitTime"] / 60, it['waitingTime'] / 60,
                    geom
                ]
        
        results.append(plan_record)
    
    # Get result
    res_df = GeoDataFrame(pd.DataFrame(results, columns=[
        "iid", "ffid", "minutes", "walkmin", "tranmin", "waitmin", "geom"
    ]), crs='EPSG:4326', geometry="geom")

    if out_epsg and out_epsg != 4326:
        res_df = df_prj(res_df, out_epsg)
    
    return res_df, error_logs
