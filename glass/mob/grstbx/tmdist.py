"""
Compute time distance between features
"""

def distance_between_catpoints(srcShp, facilitiesShp, nd, speedLimitCol,
                     onewayCol, outshp):
    """
    Path bet points
    
    TODO: Work with files with cat
    """
    
    import os
    from glass.pys.oss   import fprop
    from glass.pys.tm import now_as_str
    from glass.wenv.grs  import run_grass
    from glass.dtt.mge    import shps_to_shp
    from glass.prop.feat import feat_count
    
    # Merge Source points and Facilities into the same Feature Class
    SRC_NFEAT      = feat_count(srcShp, gisApi='pandas')
    FACILITY_NFEAT = feat_count(facilitiesShp, gisApi='pandas')

    ws, loc = os.path.dirname(outshp), now_as_str()
    
    POINTS = shps_to_shp([srcShp, facilitiesShp],
        os.path.join(ws, "points_net.shp"),
        api='pandas'
    )
    
    # Open an GRASS GIS Session
    gbase = run_grass(ws,location=loc, srs=nd)
    
    import grass.script.setup as gsetup
    gsetup.init(gbase, ws, loc, 'PERMANENT')
    
    # Import GRASS GIS Module
    from glass.it.shp          import shp_to_grs, grs_to_shp
    from glass.tbl.attr        import geomattr_to_db
    from glass.dtt.cp.grs       import copy_insame_vector
    from glass.tbl             import category
    from glass.tbl.grs         import add_table, cols_calc
    from glass.mob.grstbx.vnet import network_from_arcs
    from glass.mob.grstbx.vnet import add_pnts_to_network
    from glass.mob.grstbx.vnet import netpath
    
    # Add Data to GRASS GIS
    rdvMain = shp_to_grs(nd)
    pntShp  = shp_to_grs(POINTS)
    
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
        newNetwork, "", "ft_minutes", "tf_minutes", fprop(outshp, 'fn'),
        arcLyr=3, nodeLyr=2
    )
    
    return grs_to_shp(result, outshp, geomType="line", lyrN=3)

