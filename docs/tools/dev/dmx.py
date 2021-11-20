"""
Operations with the Google Maps Distance Matrix API and GeoPandas
"""

import pandas

def sanitizeDataCols(df, col):
    newDf = pandas.concat([
        df.drop([col], axis=1),
        df[col].apply(pandas.Series)
    ], axis=1)
        
    newDf.drop("status", axis=1, inplace=True)
        
    newDf = pandas.concat([
        newDf.drop(["distance"], axis=1),
        newDf["distance"].apply(pandas.Series)
    ], axis=1)
        
    newDf.drop("text", axis=1, inplace=True)
    newDf.rename(columns={"value" : "{}_distance".format(col)}, inplace=True)
        
    newDf = pandas.concat([
        newDf.drop(["duration"], axis=1),
        newDf["duration"].apply(pandas.Series)
    ], axis=1)
        
    newDf.drop("text", axis=1,  inplace=True)
    newDf.rename(columns={"value" : "{}_duration".format(col)}, inplace=True)
        
    return newDf

def dist_matrix_by_shp(oShp, dShp, oEpsg, dEpsg, result, transMode=None):
    """
    Create distance matrix using shapes and Google Maps API
    
    - Uses my first API_KEY
    """
    
    import time;             import pandas
    from glass.ng.rd           import tbl_to_obj
    from glass.df.split       import df_split
    from glass.g.prj         import proj
    from glass.pys.df.fld     import listval_to_newcols
    from glass.g.prop.feat   import get_gtype
    from glass.pys.df.mng     import merge_df
    from glass.adv.glg.distmx import dist_matrix
    from glass.ng.wt          import obj_to_tbl
    from glass.pys.df.to      import df_to_list
    from glass.pys.oss        import fprop
    
    # Origins and Destionations to GeoDataframe
    originsDf = tbl_to_obj(oShp); destnatDf = tbl_to_obj(dShp)
    
    # Check Geometries type - shapes should be of type point
    originsGeom = get_gtype(originsDf, gisApi='pandas')
    destGeom    = get_gtype(destnatDf, gisApi='pandas')
    if (originsGeom != 'Point' and originsGeom != 'MultiPoint') or \
        (destGeom != 'Point' and destGeom != 'MultiPoint'):
        raise ValueError('All input geometries must be of type point')
    
    # Re-project GeoDataframes if needed
    originsDf = originsDf if oEpsg == 4326 else proj(
        originsDf, None, 4326, gisApi='pandas')
    
    destnatDf = destnatDf if dEpsg == 4326 else proj(
        destnatDf, None, 4326, gisApi='pandas')
    
    # Geom to Field as str
    originsDf["geom"] = originsDf["geometry"].y.astype(str) + "," + \
        originsDf["geometry"].x.astype(str)
    
    destnatDf["geom"] = destnatDf["geometry"].y.astype(str) + "," + \
        destnatDf["geometry"].x.astype(str)
    
    originsDf["old_fid"] = originsDf.index
    destnatDf["old_fid"] = destnatDf.index
    
    # Split Destinations
    lstOrigins  = df_split(originsDf, 95, nrows=True)
    for odf in lstOrigins:
        odf.reset_index(inplace=True)
    
    lstDestinations = df_to_list(destnatDf)
    RESULTS = []
    for destino in lstDestinations:
        for oDf in lstOrigins:
            matrix = dist_matrix(
                str(oDf.geom.str.cat(sep="|")),
                str(destino["geom"]),
                oDf.shape[0], 1, transport_mode=transMode,
                useKey='AIzaSyAmyPmqtxD20urqtpCpn4ER74a6J4N403k'
            )
            
            matrix = pandas.DataFrame(matrix)
            matrix = listval_to_newcols(matrix, "elements")
            
            matrix = matrix.merge(
                oDf, how='inner', left_index=True, right_index=True)
            
            matrix.rename(columns={
                'old_fid': "fid_origin", 0 : "cost"}, inplace=True)
            
            matrix["fid_destin"] = destino['old_fid']
            
            RESULTS.append(matrix)
            
            time.sleep(5)
    
    # Join all dataframes
    RESULT = merge_df(RESULTS, ignIndex=False)
    RESULT = sanitizeDataCols(RESULT, "cost")
    
    RESULT.drop([
        x for x in originsDf.columns.values if x != "geometry" and x != "old_fid"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "origin_geom"}, inplace=True)
    
    RESULT = RESULT.merge(
        destnatDf, how='inner',
        left_on=["fid_destin"], right_on=["old_fid"]
    ); RESULT.drop([
        x for x in destnatDf.columns.values if x != "geometry"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "destin_geom"}, inplace=True)
    
    RESULT["origin_geom"] = RESULT.origin_geom.astype(str)
    RESULT["destin_geom"] = RESULT.destin_geom.astype(str)
    
    obj_to_tbl(RESULT, result, sheetsName=fprop(result, 'fn'))
    
    return result


def dist_matrix_using_shp(originsShp, destinationsShp, originsEpsg,
                          destinationsEpsg, outTable, transMode=None):
    """
    Create a distance matrix using shapes and Google Maps API
    """
    
    import time
    from threading           import Thread
    from glass.g.prj         import proj
    from glass.g.prop.feat   import get_gtype
    from glass.df.split       import df_split
    from glass.df.mng         import merge_df
    from glass.ng.rd             import tbl_to_obj
    from glass.ng.wt          import obj_to_tbl
    from glass.adv.glg        import get_keys
    from glass.adv.glg.distmx import dist_matrix
    
    # Origins and Destionations to GeoDataframe
    originsDf = tbl_to_obj(     originsShp)
    destnatDf = tbl_to_obj(destinationsShp)
    
    # Check Geometries type - shapes should be of type point
    originsGeom = get_gtype(originsDf, gisApi='pandas')
    destGeom    = get_gtype(destnatDf, gisApi='pandas')
    if (originsGeom != 'Point' and originsGeom != 'MultiPoint') or \
        (destGeom != 'Point' and destGeom != 'MultiPoint'):
        raise ValueError('All input geometries must be of type point')
    
    # Re-project GeoDataframes if needed
    originsDf = originsDf if originsEpsg == 4326 else proj(
        originsDf, None, 4326, gisApi='pandas')
    
    destnatDf = destnatDf if destinationsEpsg == 4326 else proj(
        destnatDf, None, 4326, gisAPi='pandas')
    
    # Geom to Field as str
    originsDf["geom"] = originsDf["geometry"].y.astype(str) + "," + \
        originsDf["geometry"].x.astype(str)
    
    destnatDf["geom"] = destnatDf["geometry"].y.astype(str) + "," + \
        destnatDf["geometry"].x.astype(str)
    
    originsDf["old_fid"] = originsDf.index
    destnatDf["old_fid"] = destnatDf.index
    
    # Split destinations DataFrame into Dafaframes with
    lst_destinos = df_split(destnatDf, 10, nrows=True)
    
    # Get Keys
    KEYS         = get_keys()
    lst_keys     = KEYS["key"].tolist()
    origensByKey = df_split(originsDf, KEYS.shape[0])
    
    if len(origensByKey) == len(lst_keys) + 1:
        origensByKey[-2] = origensByKey[-2].append(origensByKey[-1])
        del origensByKey[-1]
    
    # Produce matrix for each origins in origensByKey
    results = []
    def get_matrix(origins, key):
        subOrigins = df_split(origins, 10, nrows=True)
        
        for df in subOrigins:
            for __df in lst_destinos:
                matrix = dist_matrix(
                    str(df.geom.str.cat(sep="|")),
                    str(__df.geom.str.cat(sep="|")),
                    df.shape[0], __df.shape[0],
                    transport_mode=transMode,
                    useKey=str(key)
                )
                
                matrix = pandas.DataFrame(matrix)
                matrix = pandas.concat([
                    matrix.drop(["elements"], axis=1),
                    matrix["elements"].apply(pandas.Series)
                ], axis=1)
                
                originsFID = df.old_fid.tolist()
                destinaFID = __df.old_fid.tolist()
                
                mm = []
                for i in range(len(originsFID)):
                    for e in range(len(destinaFID)):
                        ll = [originsFID[i], destinaFID[e], matrix.iloc[i, e]]
                        mm.append(ll)
                
                Fmatrix = pandas.DataFrame(
                    mm, columns=["fid_origin", "fid_destin", "cost"])
                
                results.append(Fmatrix)
                
                time.sleep(5)
    
    # Create threads
    thrds = []
    i     = 1
    
    for df in origensByKey:
        thrds.append(Thread(
            name="tk{}".format(str(i)), target=get_matrix,
            args=(df, lst_keys[i - 1])
        ))
        i += 1
    
    # Start all threads
    for thr in thrds:
        thr.start()
    
    # Wait for all threads to finish
    for thr in thrds:
        thr.join()
    
    # Join all dataframes
    RESULT = merge_df(results, ignIndex=False)
    RESULT = sanitizeDataCols(RESULT, "cost")
    
    RESULT = RESULT.merge(
        originsDf, how='inner',
        left_on=["fid_origin"], right_on=["old_fid"]
    ); RESULT.drop([
        x for x in originsDf.columns.values if x != "geometry"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "origin_geom"}, inplace=True)
    
    RESULT = RESULT.merge(
        destnatDf, how='inner',
        left_on=["fid_destin"], right_on=["old_fid"]
    ); RESULT.drop([
        x for x in destnatDf.columns.values if x != "geometry"],
        axis=1, inplace=True
    ); RESULT.rename(columns={"geometry" : "destin_geom"}, inplace=True)
    
    RESULT["origin_geom"] = RESULT.origin_geom.astype(str)
    RESULT["destin_geom"] = RESULT.destin_geom.astype(str)
    
    return obj_to_tbl(RESULT, outTable)


def pnt_to_facility(pnt, pntSrs, facilities, facSrs,
                    transMode="driving"):
    """
    Calculate distance between points and the nearest facility.
    
    # TODO: Add the possibility to save the path between origins and
    destinations
    """
    
    import os;                import time
    from glass.ng.rd          import tbl_to_obj
    from glass.g.it.pd        import df_to_geodf
    from glass.g.prj          import proj
    from glass.g.prop.feat    import get_gtype
    from glass.pys.oss        import fprop
    from glass.pys.df.to      import df_to_dict, dict_to_df
    from glass.g.wt.shp       import df_to_shp
    from glass.adv.glg.distmx import dist_matrix
    
    # Convert SHPs to GeoDataFrame
    pntDf = tbl_to_obj(pnt); facil = tbl_to_obj(facilities)
    
    # Check if SHPs are points
    originsGeom = get_gtype(pntDf, geomCol="geometry", gisApi='pandas')
    if originsGeom != 'Point' and originsGeom != 'MultiPoint':
        raise ValueError('All input geometry must be of type point')
    
    destGeom = get_gtype(facil, geomCol="geometry", gisApi='pandas')
    if destGeom != 'Point' and destGeom != 'MultiPoint':
        raise ValueError('All input geometry must be of type point')
    
    # Re-Project if necessary
    pntDf = pntDf if pntSrs == 4326 else proj(pntDf, None, 4326, gisApi='pandas')
    facil = facil if facSrs == 4326 else proj(facil, None, 4326, gisApi='pandas')
    
    # Coords to cols as str
    pntDf["geom"] = pntDf["geometry"].y.astype(str) + "," + \
        pntDf["geometry"].x.astype(str)
    
    facil["geom"] = facil["geometry"].y.astype(str) + "," + \
        facil["geometry"].y.astype(str)
    
    # Get distance between points and nearest facility
    pntDict = df_to_dict(pntDf)
    
    for idx in pntDict:
        destStr = str(facil["geom"].str.cat(sep="|"))
        
        glg_resp = dist_matrix(
            pntDict[idx]["geom"], destStr,
            1, int(facil.shape[0]), transport_mode=transMode
        )
        
        matrix = pandas.DataFrame(glg_resp[0]["elements"])
        
        matrix.drop(["status", "distance"], axis=1, inplace=True)
        matrix = pandas.concat([
            matrix.drop(["duration"], axis=1),
            matrix["duration"].apply(pandas.Series)
        ], axis=1)
        
        matrix.drop("text", axis=1, inplace=True)
        matrix.rename(columns={"value": "duration"}, inplace=True)
        
        pntDict[idx]["duration"] = matrix.duration.min() / 60.0
    
    pntDf = dict_to_df(pntDict)
    pntDf = df_to_geodf(pntDf, "geometry", 4326)
    
    if pntSrs != 4326:
        pntDf = proj(pntDf, None, pntSrs, gisApi='pandas')
    
    df_to_shp(pntDf, os.path.join(
        os.path.dirname(pnt), "{}_{}.shp".format(
            fprop(pnt, 'fn'), "result"
        )
    ))
    
    return pntDf

