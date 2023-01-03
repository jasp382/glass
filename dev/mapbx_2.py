"""
MapBox API Tools
"""

def matrix_od(originsShp, destinationShp, originsEpsg, destinationEpsg,
              resultShp, modeTrans="driving"):
    """
    Use Pandas to Retrieve data from MapBox Matrix OD Service
    """
    
    import time
    from threading           import Thread
    from glass.adv.mob.mapbx import get_keys,matrix
    from glass.rd         import tbl_to_obj
    from glass.df.split      import df_split
    from glass.df.fld        import listval_to_newcols
    from glass.tbl.col     import pointxy_to_cols
    from glass.prj       import proj
    from glass.pd import merge_df
    from glass.prop.feat   import get_gtype
    from glass.wt.shp    import df_to_shp
    
    # Data to GeoDataFrame
    origens  = tbl_to_obj(    originsShp)
    destinos = tbl_to_obj(destinationShp)
    
    # Check if SHPs are points
    inGeomType = get_gtype(origens, geomCol="geometry", gisApi='pandas')
    
    if inGeomType != 'Point' and inGeomType != 'MultiPoint':
        raise ValueError('The input geometry must be of type point')
    
    inGeomType = get_gtype(destinos, geomCol="geometry", gisApi='pandas')
    
    if inGeomType != 'Point' and inGeomType != 'MultiPoint':
        raise ValueError('The input geometry must be of type point')
    
    # Re-Project data to WGS
    if originsEpsg != 4326:
        origens = proj(origens, None, 4326, api='pandas')
    
    if destinationEpsg != 4326:
        destinos = proj(destinos, None, 4326, api='pandas')
    
    origens = pointxy_to_cols(
        origens, geomCol="geometry",
        colX="longitude", colY="latitude"
    ); destinos = pointxy_to_cols(
        destinos, geomCol="geometry",
        colX="longitude", colY="latitude"
    )
    
    # Prepare coordinates Str
    origens["location"]  = origens.longitude.astype(str) \
        + "," + origens.latitude.astype(str)
    
    destinos["location"] = destinos.longitude.astype(str) \
        + "," + destinos.latitude.astype(str)
    
    # Split destinations DataFrame into Dafaframes with
    # 24 rows
    lst_destinos = df_split(destinos, 24, nrows=True)
    
    # Get Keys to use
    KEYS = get_keys()
    # Split origins by key
    origensByKey = df_split(origens, KEYS.shape[0])
    
    lst_keys= KEYS["key"].tolist()
    
    # Produce matrix
    results = []
    def get_matrix(origins, key):
        def def_apply(row):
            rowResults = []
            for df in lst_destinos:
                strDest = df.location.str.cat(sep=";")
                
                strLocations = row["location"] + ";" + strDest
                
                dados = matrix(
                    strLocations, idxSources="0",
                    idxDestinations=";".join([str(i) for i in range(1, df.shape[0] + 1)]),
                    useKey=key, modeTransportation=modeTrans
                )
                time.sleep(5)
                
                rowResults += dados["durations"][0]
            
            row["od_matrix"] = rowResults
            
            return row
        
        newOrigins = origins.apply(
            lambda x: def_apply(x), axis=1
        )
        
        results.append(newOrigins)
    
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
    
    RESULT = listval_to_newcols(RESULT, "od_matrix")
    
    RESULT.rename(
        columns={
            c: f"dest_{c}"
            for c in RESULT.columns.values if type(c) == int
        }, inplace=True
    )
    
    if originsEpsg != 4326:
        RESULT = proj(RESULT, None, originsEpsg, api='pandas')
    
    return df_to_shp(RESULT, resultShp)


    
    return results