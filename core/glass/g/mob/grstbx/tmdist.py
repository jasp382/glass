"""
Compute time distance between features
"""

def distance_between_catpoints(srcShp, facilitiesShp, networkShp, speedLimitCol,
                     onewayCol, grsWorkspace, grsLocation, outputShp):
    """
    Path bet points
    
    TODO: Work with files with cat
    """
    
    import os
    from glass.pys.oss            import fprop
    from glass.g.wenv.grs       import run_grass
    from glass.g.dp.mge import shps_to_shp
    from glass.g.prop.feat      import feat_count
    
    # Merge Source points and Facilities into the same Feature Class
    SRC_NFEAT      = feat_count(srcShp, gisApi='pandas')
    FACILITY_NFEAT = feat_count(facilitiesShp, gisApi='pandas')
    
    POINTS = shps_to_shp([srcShp, facilitiesShp],
        os.path.join(os.path.dirname(outputShp), "points_net.shp"),
        api='pandas'
    )
    
    # Open an GRASS GIS Session
    gbase = run_grass(
        grsWorkspace, grassBIN="grass76",
        location=grsLocation, srs=networkShp
    )
    
    import grass.script       as grass
    import grass.script.setup as gsetup
    gsetup.init(gbase, grsWorkspace, grsLocation, 'PERMANENT')
    
    # Import GRASS GIS Module
    from glass.g.it.shp          import shp_to_grs, grs_to_shp
    from glass.g.tbl.attr        import geomattr_to_db
    from glass.g.cp              import copy_insame_vector
    from glass.g.tbl             import category
    from glass.g.tbl.grs         import add_table
    from glass.g.tbl.col         import cols_calc
    from glass.g.mob.grstbx.vnet import network_from_arcs
    from glass.g.mob.grstbx.vnet import add_pnts_to_network
    from glass.g.mob.grstbx.vnet import netpath
    
    # Add Data to GRASS GIS
    rdvMain = shp_to_grs(networkShp, fprop(
        networkShp, 'fn', forceLower=True))
    pntShp  = shp_to_grs(POINTS, "points_net")
    
    """Get closest facility layer:"""
    # Connect Points to Network
    newNetwork = add_pnts_to_network(rdvMain, pntShp, "rdv_points")
    
    # Sanitize Network Table and Cost Columns
    newNetwork = category(
        newNetwork, "rdv_points_time", "add",
        LyrN="3", geomType="line"
    )
    
    add_table(newNetwork, (
        "cat integer,kph double precision,length double precision,"
        "ft_minutes double precision,"
        "tf_minutes double precision,oneway text"
    ), lyrN=3)
    
    copy_insame_vector(newNetwork, "kph", speedLimitCol, 3, geomType="line")
    copy_insame_vector(newNetwork, "oneway",  onewayCol, 3, geomType="line")
    
    geomattr_to_db(
        newNetwork, "length", "length", "line",
        createCol=False, unit="meters", lyrN=3
    )
    
    cols_calc(newNetwork, "kph", "3.6", "kph IS NULL", lyrN=3)
    cols_calc(
        newNetwork, "ft_minutes",
        "(length * 60) / (kph * 1000.0)",
        "ft_minutes IS NULL", lyrN=3
    )
    cols_calc(
        newNetwork, "tf_minutes",
        "(length * 60) / (kph * 1000.0)",
        "tf_minutes IS NULL", lyrN=3
    )
    
    # Exagerate Oneway's
    cols_calc(newNetwork, "ft_minutes", "1000", "oneway = 'TF'", lyrN=3)
    cols_calc(newNetwork, "tf_minutes", "1000", "oneway = 'FT'", lyrN=3)
    
    # Produce result
    result = netpath(
        newNetwork, "", "ft_minutes", "tf_minutes", fprop(outputShp, 'fn'),
        arcLyr=3, nodeLyr=2
    )
    
    return grs_to_shp(result, outputShp, geomType="line", lyrN=3)

