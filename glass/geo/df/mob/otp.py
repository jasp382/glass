"""
OpenTripPlanner
"""

def otp_closest_facility(incidents, facilities, hourday, date, output):
    """
    Closest Facility using OTP
    """

    import requests
    import polyline
    import os
    import pandas as pd
    from shapely.geometry import LineString
    from shapely.ops      import linemerge
    from geopandas        import GeoDataFrame

    from glass.cons.otp      import PLANNER_URL
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.geo.obj.prj   import df_prj
    from glass.geo.prop.prj  import get_epsg_shp
    from glass.dct.geo.toshp import obj_to_shp
    from glass.pys.oss       import fprop

    # Open Data
    incidents_df  = df_prj(shp_to_obj(incidents), 4326)
    facilities_df = df_prj(shp_to_obj(facilities), 4326)

    error_logs = []
    # Results
    # incident_id, facility_id, minutes, walkmin, tranmin, waitmin, geom
    results = []

    for i, r in incidents_df.iterrows():
        duration    = None
        plan_record = None

        for e, _r in facilities_df.iterrows():
            fromPlace = str(r.geometry.y) + ',' + str(r.geometry.x)
            toPlace   = str(_r.geometry.y) + ',' + str(_r.geometry.x)

            resp = requests.get(PLANNER_URL, params={
                'fromPlace'       : fromPlace,
                'toPlace'         : toPlace,
                'time'            : hourday,
                'date'            : date,
                'mode'            : 'TRANSIT,WALK',
                'maxWalkDistance' : 50000,
                'arriveBy'        : 'false',
                'numItineraries'  : 1
            }, headers={'accept'  : 'application/json'})

            # Get Response JSON
            data = resp.json()

            if "error" in data:
                error_logs.append([i, e, data["error"]])
                continue

            # Get Iteneraries
            it = data['plan']["itineraries"][0]

            if not duration or duration > it["duration"]:
                duration = it["duration"]

                # Get intenerary geometry
                geoms = [LineString(polyline.decode(p["legGeometry"]["points"], geojson=True)) for p in it['legs']]
                
                geom = linemerge(geoms)

                plan_record = [
                    i, e, it["duration"] / 60, it["walkTime"] / 60,
                    it["transitTime"] / 60, it['waitingTime'] / 60,
                    geom
                ]
        
        results.append(plan_record)
    
    # Export result
    res_df = GeoDataFrame(pd.DataFrame(results, columns=[
        "iid", "ffid", "minutes", "walkmin", "tranmin", "waitmin", "geom"
    ]), crs='EPSG:4326', geometry="geom")

    out_epsg = get_epsg_shp(incidents)

    if out_epsg != 4326:
        res_df = df_prj(res_df, out_epsg)
    
    obj_to_shp(res_df, "geom", out_epsg, output)

    return output


def otp_servarea(facilities, hourday, date, breaks, output):
    """
    OTP Service Area
    """

    import requests
    import os
    from glass.cons.otp import ISO_URL
    from glass.dct.geo.fmshp import shp_to_obj
    from glass.geo.obj.prj import df_prj
    from glass.geo.prop.prj import get_epsg_shp
    from glass.dct.geo.toshp import obj_to_shp
    from glass.pys.oss import fprop
    from glass.geo.obj.pd import json_obj_to_geodf
    from glass.dp.pd import merge_df
    from glass.pys import obj_to_lst

    breaks = obj_to_lst(breaks)

    # Open Data
    facilities_df = df_prj(shp_to_obj(facilities), 4326)

    # Place request parameters
    get_params = [
        ('mode', 'WALK,TRANSIT'),
        ('date', date),
        ('time', hourday),
        ('maxWalkDistance', 50000)
    ]

    breaks.sort()

    for b in breaks:
        get_params.append(('cutoffSec', b))
    
    # Do the math
    error_logs = []
    results    = []

    for i, r in facilities_df.iterrows():
        fromPlace = str(r.geometry.y) + ',' + str(r.geometry.x)

        if not i:
            get_params.append(('fromPlace', fromPlace))
        else:
            get_params[-1] = ('fromPlace', fromPlace)
        
        resp = requests.get(ISO_URL, get_params, headers={'accept' : 'application/json'})

        try:
            data = resp.json()
        except:
            error_logs.append([i, 'Cannot retrieve JSON Response'])
            continue

        gdf = json_obj_to_geodf(data, 4326)
        gdf['ffid'] = i

        results.append(gdf)
    
    # Merge all Isochrones
    df_res = merge_df(results)

    out_epsg = get_epsg_shp(facilities)

    if out_epsg != 4326:
        df_res = df_prj(df_res, out_epsg)
    
    obj_to_shp(df_res, "geometry", out_epsg, output)

    # Write logs
    if len(error_logs):
        with open(os.path.join(os.path.dirname(output), fprop(output, 'fn') + '.log.txt'), 'w') as txt:
            for i in error_logs:
                txt.write((
                    "Facility_id: {}\n"
                    "ERROR message:\n"
                    "{}\n"
                    "\n\n\n\n\n\n"
                ).format(str(i[0]), i[1]))

    return output

