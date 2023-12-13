"""
Contributions processing to find fire locations after
"""

from glass.it.pd import obj_to_geodf


def ctb_by_geom(cdf, delcols=None):
    """
    Create Contributions dataframes for each type
    of geometry
    """

    if delcols:
        cdf.drop(delcols, axis=1, inplace=True)
    
    # Get Dataframe for each type of geometry
    dfs = {
        # Main Geometry DataFrame
        "geom"     : cdf,
        # Get usergeom dataframe
        "usergeom" : cdf[~cdf.usergeom.isna()],
        # Get geom back front dataframe
        "geombf"   : cdf[~cdf.geombf.isna()],
        # Centroids dataframes - empty for now
        "geomc"    : cdf.copy(deep=True),
        "geombfc"  : cdf.copy(deep=True)
    }

    dfs["usergeom"] = dfs["usergeom"].reset_index(drop=True)
    dfs["geombf"]   = dfs["geombf"].reset_index(drop=True)

    dfs["geom"].drop([
        "geombf", "usergeom", "geomc", "geombfc"
    ], axis=1, inplace=True)
    dfs["geomc"].drop([
        "geom", "geombf", "usergeom", "geombfc"
    ], axis=1, inplace=True)
    dfs["geombfc"].drop([
        "geom", "geombf", "geomc", "usergeom"
    ], axis=1, inplace=True)

    dfs["geombf"].drop([
        "geom", "usergeom", "geomc", "geombfc"
    ], axis=1, inplace=True)
    dfs["usergeom"].drop([
        "geom", "geombf", "geomc", "geombfc"
    ], axis=1, inplace=True)

    return dfs


def ctb_lstpnt_to_point(dfs, ignore=None):
    """
    Contributions multipoints to points
    """

    from glass.pd.dagg import col_list_val_to_row
    from glass.pd.cols import dictval_to_cols

    for k in dfs:
        if ignore and k in ignore: continue
        if not dfs[k].shape[0]: continue

        dfs[k] = col_list_val_to_row(dfs[k], k)
    
        dfs[k].rename(columns={k : 'dictgeom'}, inplace=True)

        dfs[k] = dictval_to_cols(dfs[k], 'dictgeom')

        dfs[k].drop(['dictgeom', 'azimute'], axis=1, inplace=True)

        if k != 'geom':
            dfs[k].rename(columns={"geom" : k}, inplace=True)
    
    return dfs


def ctb_centroids(dfs, cntr_keys):
    """
    Get Centroids for the main positions and back-front
    positions
    """

    from glass.it.pd import df_to_geodf
    from glass.prj.obj   import df_prj

    for k in cntr_keys:
        dfs[cntr_keys[k]] = dfs[k].copy()

        if not dfs[cntr_keys[k]].shape[0]:
            continue

        # To GeoDataFrame
        dfs[cntr_keys[k]] = obj_to_geodf(dfs[cntr_keys[k]], 'geom', '4326')

        # Geometry to MultiGeometry
        dfs[cntr_keys[k]] = dfs[cntr_keys[k]].dissolve(by='fid')

        dfs[cntr_keys[k]].reset_index(drop=False, inplace=True)
        dfs[cntr_keys[k]].drop(['pid', 'azimute'], axis=1, inplace=True)

        # Coordinates to planimetric
        tmpdf = df_prj(dfs[cntr_keys[k]], 3763)

        # Get Centroid
        tmpdf["geom"] = tmpdf.geom.centroid

        # Centroid to WGS 84
        dfs[cntr_keys[k]] = df_to_geodf(tmpdf, 'geom', 4326)
        dfs[cntr_keys[k]] = df_prj(tmpdf, 4326)

        # Centroid to String
        dfs[cntr_keys[k]]["geom"] = dfs[cntr_keys[k]].geom.to_wkt()
    
    return dfs

