"""
Google API tools
"""

def assign_cost_to_line(inLines, outLines, epsg):
    """
    Assign Movement Cost to Line
    """
    
    import time;              import pandas 
    from geopandas            import GeoDataFrame
    from glass.rd          import tbl_to_obj
    from glass.prj        import proj
    from glass.adv.glg.direct import pnt_to_pnt_duration
    from glass.wt.shp     import df_to_shp
    
    # Data to GeoDataFrame
    linesDf = tbl_to_obj(inLines)
    
    # Re-Project input data
    if epsg != 4326:
        linesDf = proj(linesDf, None, 4326, gisApi='pandas')
    
    def get_points(row):
        row["points"] = [pnt for pnt in row["geometry"].coords]
        
        return row
    
    linesDf = linesDf.apply(lambda x: get_points(x), axis=1)
    
    linesDict = linesDf.to_dict(orient='index')
    
    # Get All possible vertex pairs in each line
    # Get distance between the start and end of each line formed by one pair
    # Sum all distances and associate the new value to the original line
    for idx in linesDict:
        points = linesDict[idx]["points"]
        
        pairs = [
            pnt_to_pnt_duration(
                points[i-1][1], points[i-1][0],
                points[i][1], points[i][0], mode="driving"
            ) for i in range(1, len(points))
        ]
        
        time.sleep(5)
        
        linesDict[idx]["duration"] = sum(pairs)
    
    linesDff = pandas.DataFrame.from_dict(linesDict, orient='index')
    
    # Re-Project input data
    linesDff = GeoDataFrame(
        linesDff, crs={"init": "epsg:4326"}, geometry="geometry"
    )
    
    if epsg != 4326:
        linesDff = proj(linesDff, None, epsg, gisApi='pandas')
    
    linesDff.drop("points", axis=1, inplace=True)
    
    df_to_shp(linesDff, outLines)
    
    return outLines


def dist_onedest_network(pntShp, pntRouteId, networkShp, netRouteId,
                         netOrder, netDuration, srs, output):
    """
    Imagine-se uma rede cujos arcos levam a um unico destino
    Este programa calcula a distancia entre um ponto e esse destino
    em duas fases:
    * calculo da distancia ao ponto de entrada na rede mais proximo;
    * distancia entre essa entrada o destino da rede.
    
    A rede e composta por circuitos, e suposto partir-se de um ponto,
    entrar num circuito e nunca sair dele ate ao destino. O circuito
    associado a cada ponto deve constar na tabela dos pontos.
    """
    
    import pandas;            import time
    from glass.rd          import tbl_to_obj
    from glass.adv.glg.direct import pnt_to_pnt_duration
    from glass.it.pd        import df_to_geodf, pnt_dfwxy_to_geodf
    from glass.pyt.df.agg     import df_groupBy
    from glass.prj         import proj
    from glass.tbl.col      import pointxy_to_cols
    from glass.tbl.col      import geom_endpoints_to_cols
    from glass.pyt.df.fld     import distinct_of_distinct
    from glass.wt.shp      import df_to_shp
    from glass.pyt.df.to      import df_to_dict, dict_to_df
    
    netDataFrame = tbl_to_obj(networkShp)
    pntDataFrame = tbl_to_obj(pntShp)
    
    # Get entrance nodes
    netDataFrame = geom_endpoints_to_cols(netDataFrame, geomCol="geometry")
    geoEntrances = pnt_dfwxy_to_geodf(netDataFrame, "start_x", "start_y", srs)
    
    # To WGS
    if srs != 4326:
        geoEntrances = proj(geoEntrances, None, 4326, gisApi='pandas')
        pntDataFrame = proj(pntDataFrame, None, 4326, gisApi='pandas')
    
    # Get entrances by circuit
    routesEntrances = distinct_of_distinct(geoEntrances, netRouteId, netOrder)
    
    pntRelStops = pntDataFrame.merge(
        geoEntrances, how='inner',
        left_on=pntRouteId, right_on=netRouteId
    )
    
    pntRelStops = pointxy_to_cols(
        pntRelStops, geomCol="geometry",
        colX="start_x", colY="start_y"
    ); pntRelStops = pointxy_to_cols(
        pntRelStops, geomCol="geometry",
        colX="node_x", colY="node_y"
    )
    
    pntRelStopsDict = df_to_dict(pntRelStops)
    
    for idx in pntRelStopsDict:
        ape= pnt_to_pnt_duration(
            pntRelStopsDict[idx]["start_y"], pntRelStopsDict[idx]["start_x"],
            pntRelStopsDict[idx]["node_y"] , pntRelStopsDict[idx]["node_x"],
            mode="walking"
        )
        
        time.sleep(5)
        
        pntRelStopsDict[idx]["gduration"] = ape
    
    pntRelStops = dict_to_df(pntRelStopsDict)
    
    pntRelStops_gp = df_groupBy(
        pntRelStops,
        [x for x in list(pntDataFrame.columns.values) if x != "geometry"],
        STAT='MIN', STAT_FIELD="gduration"
    )
    
    pntRelStops_gp = pntRelStops_gp.merge(
        pntRelStops, how='inner',
        left_on  = list(pntRelStops_gp.columns.values),
        right_on = list(pntRelStops_gp.columns.values)
    )
    
    final_time = []
    for idx, row in pntRelStops_gp.iterrows():
        circ  = row[pntRouteId]
        order = row[netOrder]
        
        for i in range(len(routesEntrances[circ])):
            if order == routesEntrances[circ][i]:
                checkpoints = routesEntrances[circ][i:]
            
            else:
                continue
        
        timedistance = []
        for check in checkpoints:
            val = int(
                netDataFrame.loc[
                    (netDataFrame[netRouteId] == circ) & 
                    (netDataFrame[netOrder] == check), [netDuration]
                ][netDuration]
            )
            
            timedistance.append(val)
        
        final_time.append(row["gduration"] + sum(timedistance))
    
    pntRelStops_gp["final_time"] = pandas.Series(final_time)
    
    # Save result
    pntRelStops_gp.drop(["geometry_y"], axis=1, inplace=True)
    
    gd = df_to_geodf(pntRelStops_gp, "geometry_x", 4326)
    
    if srs != 4326:
        gd = proj(gd, None, srs, gisApi='pandas')
    
    df_to_shp(gd, output)
    
    return output

