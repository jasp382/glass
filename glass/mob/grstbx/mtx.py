"""
Produce things related with accessibility
"""

import os


def prod_matrix(origins, destinations, networkGrs, speedLimitCol, onewayCol,
                thrdId="1", asCmd=None):
    """
    Get Matrix Distance:
    """
    
    from glass.tbl             import category
    from glass.dtt.filter      import sel_by_attr
    from glass.tbl.col         import add_fields
    from glass.tbl.grs         import add_table, cols_calc
    from glass.mob.grstbx.vnet import pnts_to_net
    from glass.mob.grstbx.anls import run_allpairs
    from glass.dtt.cp.grs      import copy_insame_vector
    from glass.tbl.attr        import geomattr_to_db
    from glass.dtt.mge         import shps_to_shp
    from glass.prop.feat       import feat_count
    from glass.it.shp          import shp_to_grs
    
    # Merge Origins and Destinations into the same Feature Class
    ORIGINS_NFEAT      = feat_count(origins, gisApi='pandas')
    DESTINATIONS_NFEAT = feat_count(destinations, gisApi='pandas')
    
    ORIGINS_DESTINATIONS = shps_to_shp(
        [origins, destinations], os.path.join(
            os.path.dirname(origins), f"points_od_{thrdId}.shp"
        ), api='pandas'
    )
    
    pointsGrs  = shp_to_grs(
        ORIGINS_DESTINATIONS, f"points_od_{thrdId}", asCMD=asCmd)
    
    # Connect Points to Network
    newNetwork = pnts_to_net(
        networkGrs, pointsGrs, f"rdv_points_{thrdId}", asCMD=asCmd
    )
    
    # Sanitize Network Table and Cost Columns
    newNetwork = category(
        newNetwork, f"rdv_points_time_{thrdId}", "add",
        LyrN="3", geomType="line", asCMD=asCmd
    )
    
    add_table(newNetwork, (
        "cat integer,kph double precision,length double precision,"
        "ft_minutes double precision,"
        "tf_minutes double precision,oneway text"
    ), lyrN=3, asCMD=asCmd)
    
    copy_insame_vector(
        newNetwork, "kph", speedLimitCol, 3, geomType="line", asCMD=asCmd
    ); copy_insame_vector(
        newNetwork, "oneway",  onewayCol, 3, geomType="line", asCMD=asCmd)
    
    geomattr_to_db(
        newNetwork, "length", "length", "line",
        createCol=False, unit="meters", lyrN=3, ascmd=asCmd
    )
    
    cols_calc(newNetwork, "kph", "3.6",  "kph IS NULL", lyrN=3, ascmd=asCmd)
    cols_calc(newNetwork, "kph", "3.6", "oneway = 'N'", lyrN=3, ascmd=asCmd)
    cols_calc(
        newNetwork, "ft_minutes",
        "(length * 60) / (kph * 1000.0)",
        "ft_minutes IS NULL", lyrN=3, ascmd=asCmd
    ); cols_calc(
        newNetwork, "tf_minutes",
        "(length * 60) / (kph * 1000.0)",
        "tf_minutes IS NULL", lyrN=3, ascmd=asCmd
    )
    
    # Exagerate Oneway's
    cols_calc(
        newNetwork, "ft_minutes", "1000", "oneway = 'TF'", lyrN=3, ascmd=asCmd
    ); cols_calc(
        newNetwork, "tf_minutes", "1000", "oneway = 'FT'", lyrN=3, ascmd=asCmd)
    
    # Produce matrix
    matrix = run_allpairs(
        newNetwork, "ft_minutes", "tf_minutes",
        f'result_{thrdId}', arcLyr=3, nodeLyr=2, asCMD=asCmd
    )
    
    # Exclude unwanted OD Pairs
    q = "({}) AND ({})".format(
        " OR ".join(["from_cat={}".format(
            str(i+1)) for i in range(ORIGINS_NFEAT)
        ]),
        " OR ".join(["to_cat={}".format(
            str(ORIGINS_NFEAT + i + 1)) for i in range(DESTINATIONS_NFEAT)
        ])
    )
    
    matrix_sel = sel_by_attr(
        matrix, q, f"sel_{matrix}",
        geomType="line", lyrN=3, asCMD=asCmd
    )
    
    add_fields(matrix_sel, "from_fid", "INTEGER", lyrN=3, asCMD=asCmd)
    add_fields(matrix_sel,   "to_fid", "INTEGER", lyrN=3, asCMD=asCmd)
    
    cols_calc(
        matrix_sel, "from_fid",
        "from_cat - 1", "from_fid IS NULL", lyrN=3, ascmd=asCmd
    )
    cols_calc(
        matrix_sel, "to_fid", 
        f"to_cat - {str(ORIGINS_NFEAT)} - 1",
        "to_fid IS NULL", lyrN=3, ascmd=asCmd
    )
    
    return matrix_sel


def matrix_od(origins, destinations, rdv, speedLimitCol, onewayCol,
              oshp):
    """
    Produce matrix OD using GRASS GIS
    """
    
    from glass.pys.oss  import fprop
    from glass.wenv.grs import run_grass

    ws, loc = os.path.dirname(oshp), f"loc_{fprop(oshp, 'fn')}"
    
    # Open an GRASS GIS Session
    gbase = run_grass(ws, location=loc, srs=rdv)
    
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, ws, loc, 'PERMANENT')
    
    # Import GRASS GIS Module
    from glass.it.shp import shp_to_grs, grs_to_shp
    
    # Add Data to GRASS GIS
    rdvgrs = shp_to_grs(rdv, fprop(rdv, 'fn', forceLower=True))
    
    """Get matrix distance:"""
    MATRIX_OD = prod_matrix(
        origins, destinations, rdvgrs, speedLimitCol, onewayCol
    )
    
    return grs_to_shp(MATRIX_OD, oshp, "line", lyrN=3)


def thrd_matrix_od(origins, destinationShp, network, costCol, oneway, output):
    """
    Produce matrix OD using GRASS GIS - Thread MODE
    
    PROBLEM:
    * O programa baralha-se todo porque ha muitas sessoes do grass a serem 
    executadas. E preciso verificar se e possivel segregar as varias sessoes
    do grass
    """
    
    from threading      import Thread
    from glass.wenv.grs import run_grass
    from glass.pys.oss  import fprop, mkdir
    from glass.dtt.mge   import shps_to_shp
    from glass.dtt.split import splitShp_by_range

    ws = os.path.dirname(output)
    loc = f"loc_{fprop(output, 'fn')}"
    
    # SPLIT ORIGINS IN PARTS
    originsFld = mkdir(os.path.join(ws, loc, 'origins_parts'))
    
    originsList = splitShp_by_range(origins, 100, originsFld)
    
    gbase = run_grass(ws, location=loc, srs=network)
    
    import grass.script.setup as gsetup
    
    gsetup.init(gbase, ws, loc, 'PERMANENT')
    
    from glass.it.shp import shp_to_grs

    # Add Data to GRASS GIS
    rdvMain = shp_to_grs(network, fprop(
        network, 'fn', forceLower=True), asCMD=True)
    
    RESULTS = []
    R_FOLDER = mkdir(os.path.join(ws, loc, 'res_parts'))
    
    def __prod_mtxod(O, D, THRD):
        result_part = prod_matrix(
            O, D, rdvMain, costCol, oneway, thrdId=THRD, asCmd=True
        )
        
        shp = shp_to_grs(
            result_part, os.path.join(R_FOLDER, result_part + '.shp'),
            geom_type="line", lyrN=3, asCMD=True
        )
        
        RESULTS.append(shp)
    
    thrds = []
    for i in range(len(originsList)):
        thrds.append(Thread(
            name='tk-{}'.format(str(i)), target=__prod_mtxod,
            args=(originsList[i], destinationShp, str(i))
        ))
    
    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    shps_to_shp(RESULTS, output, api='pandas')
    
    return output


def bash_matrix_od(origins, destinationShp, network, costCol, oneway,
                   grsWork, output):
    """
    Produce matrix OD using GRASS GIS - BASH MODE
    """
    
    from glass.wenv.grs import run_grass
    from glass.pys.oss  import fprop, mkdir
    from glass.dtt.split import splitShp_by_range
    from glass.dtt.mge   import shps_to_shp
    
    # SPLIT ORIGINS IN PARTS
    originsFld = mkdir(os.path.join(grsWork, 'origins_parts'))
    
    originsList = splitShp_by_range(origins, 100, originsFld)
    
    # Open an GRASS GIS Session
    gbase = run_grass(grsWork, location='location', srs=network)

    import grass.script.setup as gsetup
    
    RESULTS = []
    R_FOLDER = mkdir(os.path.join(grsWork, 'res_parts'))
    
    for e in range(len(originsList)):
        gsetup.init(gbase, grsWork, f"grs_loc_{e}", 'PERMANENT')
        
        from glass.it.shp import shp_to_grs, grs_to_shp
    
        # Add Data to GRASS GIS
        rdvMain = shp_to_grs(network, fprop(
            network, 'fn', forceLower=True))
        
        # Produce Matrix
        result_part = prod_matrix(
            originsList[e], destinationShp, rdvMain, costCol, oneway
        )
        
        # Export Result
        shp = grs_to_shp(
            result_part, os.path.join(R_FOLDER, f"{result_part}.shp"),
            geom_type="line", lyrN=3
        )
        
        RESULTS.append(shp)
    
    shps_to_shp(RESULTS, output, api='pandas')
    
    return output

