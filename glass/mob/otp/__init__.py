"""
OpenTripPlanner
"""

def otp_closest_facility(incidents, facilities, hourday, date, output):
    """
    Closest Facility using OTP
    """

    
    import os
    from glass.rd.shp      import shp_to_obj
    from glass.prop.prj    import shp_epsg
    from glass.wt.shp      import obj_to_shp
    from glass.pys.oss       import fprop
    from glass.prj.obj     import df_prj
    from glass.mob.otp.log import clsfacility

    # Open Data
    incidents_df  = df_prj(shp_to_obj(incidents), 4326)
    facilities_df = df_prj(shp_to_obj(facilities), 4326)

    # Run closest facility
    out_epsg = shp_epsg(incidents)
    res, logs = clsfacility(
        incidents_df, facilities_df, hourday, date,
        out_epsg=out_epsg
    )

    # Export result
    obj_to_shp(res, "geom", out_epsg, output)

    # Write logs
    if len(logs):
        with open(os.path.join(os.path.dirname(output), fprop(output, 'fn') + '_log.txt'), 'w') as txt:
            for i in logs:
                txt.write((
                    "Incident_id: {}\n"
                    "Facility_id: {}\n"
                    "ERROR message:\n"
                    "{}\n"
                    "\n\n\n\n\n\n"
                ).format(str(i[0]), str(i[1]), str(i[2])))


    return output


def otp_cf_based_on_rel(incidents, group_incidents_col,
    facilities, facilities_id, rel_inc_fac, sheet, group_fk, facilities_fk,
    hour, day, output):
    """
    Calculate time travel considering specific facilities
    for each group of incidents

    Relations between incidents and facilities are in a auxiliar table (rel_inc_fac).
    Auxiliar table must be a xlsx file
    """

    import os
    import pandas as pd
    from glass.rd          import tbl_to_obj
    from glass.rd.shp      import shp_to_obj
    from glass.wt.shp      import obj_to_shp
    from glass.mob.otp.log import clsfacility
    from glass.prop.prj    import shp_epsg
    from glass.dtt.mge.pd  import merge_df
    from glass.pys.oss     import fprop
    from glass.prj.obj     import df_prj

    # Avoid problems when facilities_id == facilities_fk
    facilities_fk = facilities_fk + '_fk' if facilities_id == facilities_fk else \
        facilities_fk

    # Open data
    idf = df_prj(shp_to_obj(incidents), 4326)
    fdf = df_prj(shp_to_obj(facilities), 4326)

    rel_df = tbl_to_obj(rel_inc_fac, sheet=sheet)

    oepsg = shp_epsg(incidents)

    # Relate facilities with incidents groups
    fdf = fdf.merge(
        rel_df, how='inner',
        left_on=facilities_id, right_on=facilities_fk
    )

    # List Groups
    grp_df = pd.DataFrame({
        'cnttemp' : idf.groupby([group_incidents_col])[group_incidents_col].agg('count')
    }).reset_index()

    # Do calculations
    res = []
    logs = []
    for idx, row in grp_df.iterrows():
        # Get incidents for that group
        new_i = idf[idf[group_incidents_col] == row[group_incidents_col]]

        # Get facilities for that group
        new_f = fdf[fdf[group_fk] == row[group_incidents_col]]

        # calculate closest facility
        cfres, l = clsfacility(new_i, new_f, hour, day, out_epsg=oepsg)

        res.append(cfres)
        logs.extend(l)
    
    # Merge results
    out_df = merge_df(res)

    # Recovery facility id
    fdf.drop([c for c in fdf.columns.values if c != facilities_id], axis=1, inplace=True)
    out_df = out_df.merge(fdf, how='left', left_on='ffid', right_index=True)

    # Export result
    obj_to_shp(out_df, "geom", oepsg, output)

    # Write logs
    if len(logs) > 0:
        with open(os.path.join(os.path.dirname(output), fprop(output, 'fn') + '_log.txt'), 'w') as txt:
            for i in logs:
                txt.write((
                    "Incident_id: {}\n"
                    "Facility_id: {}\n"
                    "ERROR message:\n"
                    "{}\n"
                    "\n\n\n\n\n\n"
                ).format(str(i[0]), str(i[1]), str(i[2])))

    return output


def otp_servarea(facilities, hourday, date, breaks, output, vel=None):
    """
    OTP Service Area
    """

    import requests
    import os
    from glass.cons.otp   import ISO_URL
    from glass.rd.shp     import shp_to_obj
    from glass.prj.obj    import df_prj
    from glass.prop.prj   import shp_epsg
    from glass.wt.shp     import obj_to_shp
    from glass.pys.oss    import fprop
    from glass.it.pd      import json_obj_to_geodf
    from glass.dtt.mge.pd import merge_df
    from glass.pys        import obj_to_lst

    breaks = obj_to_lst(breaks)

    # Open Data
    facilities_df = df_prj(shp_to_obj(facilities), 4326)

    # Place request parameters
    get_params = [
        ('mode', 'WALK,TRANSIT'),
        ('date', date),
        ('time', hourday),
        ('maxWalkDistance', 50000),
        ('walkSpeed', 3 if not vel else vel)
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

    out_epsg = shp_epsg(facilities)

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

