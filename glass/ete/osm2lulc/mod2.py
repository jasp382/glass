"""
Rule 2 - Select Roads
"""

import datetime as dt

from glass.cons.otol import OSM_TABLES
from glass.prop.sql          import row_num

def grs_rst_roads(osmdb, lineTbl, polyTbl, LULC_CLS):
    """
    Raster Roads for GRASS
    """
    
    from glass.it.shp            import dbtbl_to_shp
    from glass.dtt.torst         import grsshp_to_grsrst as shp_to_rst
    from glass.gp.prox.bfing.sql import splite_buffer
    from glass.prop.sql          import row_num
    
    time_a = dt.datetime.now().replace(microsecond=0)
    NR = row_num(osmdb, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    roadFile = splite_buffer(
        osmdb, lineTbl, "bf_roads", "geometry", 'bfu_roads',
        #os.path.join(dataFolder, 'bf_roads.gml'),
        whrClause="roads IS NOT NULL",
        outTblIsFile=None, dissolve="ALL"
    )
    time_c = dt.datetime.now().replace(microsecond=0)
    
    #roadGrs = shp_to_grs(roadFile, "bf_roads", filterByReg=True, asCMD=True)
    roadGrs = dbtbl_to_shp(
        osmdb, roadFile, "geom", 'bf_roads',
        notTable=True, outShpIsGRASS=True, inDB='sqlite'
    )
    time_d = dt.datetime.now().replace(microsecond=0)
    roadRst = shp_to_rst(
        roadGrs, int(LULC_CLS), "rst_roads", cmd=True
    )
    time_e = dt.datetime.now().replace(microsecond=0)
    
    # Builds to GRASS and to RASTER
    NB = row_num(osmdb, polyTbl, where="building IS NOT NULL", api='sqlite')
    time_f = dt.datetime.now().replace(microsecond=0)
    
    if NB:
        from glass.rst.alg  import grsrstcalc
        from glass.rst.rcls import set_null, null_to_value
        
        buildsShp = dbtbl_to_shp(
            osmdb, polyTbl, "geom", "all_builds",
            where="building IS NOT NULL",
            notTable=True, outShpIsGRASS=True, inDB='sqlite'
        )
        time_g = dt.datetime.now().replace(microsecond=0)
        
        buildsRst = shp_to_rst(
            buildsShp, 1, "rst_builds", cmd=True
        )
        time_h = dt.datetime.now().replace(microsecond=0)
        
        # Buildings to nodata | Nodata to 0
        null_to_value(buildsRst, 0, as_cmd=True)
        time_i = dt.datetime.now().replace(microsecond=0)
        set_null(buildsRst, 1, ascmd=True)
        time_j = dt.datetime.now().replace(microsecond=0)
        
        # Do the math: roads + builds | if builds and roads at the same cell
        # cell will be null in the road layer
        roadsRes = rstcalc(f"{roadRst} + {buildsRst}", "cls_roads")
        time_l = dt.datetime.now().replace(microsecond=0)
        
        return {LULC_CLS : roadsRes}, {
            0 : ('count_rows_roads', time_b - time_a),
            1 : ('buffer_roads', time_c - time_b),
            2 : ('import_roads', time_d - time_c),
            3 : ('roads_to_rst', time_e - time_d),
            4 : ('count_build', time_f - time_e),
            5 : ('builds_to_grs', time_g - time_f),
            6 : ('builds_to_rst', time_h - time_g),
            7 : ('bnull_to_val', time_i - time_h),
            8 : ('builds_to_nd', time_j - time_i),
            9 : ('roads_build_mc', time_l - time_j)
        }
    
    else:
        return {LULC_CLS : roadRst}, {
            0 : ('count_rows_roads', time_b - time_a),
            1 : ('buffer_roads', time_c - time_b),
            2 : ('import_roads', time_d - time_c),
            3 : ('roads_to_rst', time_e - time_d),
            4 : ('count_build', time_f - time_e)
        }


def grs_vec_roads(osmdb, lineTbl, polyTbl):
    """
    Select Roads for GRASS GIS
    """
    
    from glass.prop.sql      import row_num
    from glass.it.shp        import dbtbl_to_shp
    from glass.gp.prox.bfing import _buffer
    from glass.gp.gen        import dissolve
    from glass.tbl.grs       import add_table
    
    # Roads to GRASS GIS
    time_a = dt.datetime.now().replace(microsecond=0)
    NR = row_num(osmdb, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    roadsVect = dbtbl_to_shp(
        osmdb, lineTbl, "geometry", "all_roads", where="roads IS NOT NULL",
        inDB='sqlite', outShpIsGRASS=True
    )
    time_c = dt.datetime.now().replace(microsecond=0)
    
    # Buildings to GRASS GIS
    NB = row_num(osmdb, polyTbl, where="building IS NOT NULL", api='sqlite')
    time_d = dt.datetime.now().replace(microsecond=0)
    
    if NB:
        from glass.gp.prox import grs_near as near
        from glass.tbl.grs import cols_calc
        
        builds = dbtbl_to_shp(
            osmdb, polyTbl, "geometry", "all_builds", where="building IS NOT NULL",
            filterByReg=True, inDB='sqlite', outShpIsGRASS=True
        )
        time_e = dt.datetime.now().replace(microsecond=0)
        
        near(roadsVect, builds, nearDistCol="todist", maxDist=12, as_cmd=True)
        time_f = dt.datetime.now().replace(microsecond=0)
        cols_calc(
            roadsVect, "bf_roads", "round(todist,0)",
            "\"todist > 0\"",
            lyrN=1, ascmd=True
        )
        time_g = dt.datetime.now().replace(microsecond=0)
    
    else:
        time_e = None; time_f = None; time_g = None
    
    # Run Buffer tool
    roadsBf = _buffer(
        roadsVect, "bf_roads", "bf_roads",
        api='grass', geom_type="line"
    )
    time_h = dt.datetime.now().replace(microsecond=0)
    
    # Dissolve Roads
    roadsDiss = dissolve(roadsBf, "diss_roads", "roads", api="grass")
    
    add_table(roadsDiss, None, lyrN=1, asCMD=True)
    time_i = dt.datetime.now().replace(microsecond=0)
    
    return roadsDiss, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('import_roads', time_c - time_b),
        2 : ('count_rows_build', time_d - time_c),
        3 : None if not time_e else ('import_builds', time_e - time_d),
        4 : None if not time_f else ('near_analysis', time_f - time_e),
        5 : None if not time_g else ('update_buffer_tbl', time_g - time_f),
        6 : ('buffer_roads', time_h - time_g if time_g else time_h - time_d),
        7 : ('diss_roads', time_i - time_h)
    }


def roads_fmdb(osmdb, lnhTbl, plTbl, asRst=None):
    """
    Roads processing using PostGIS
    """
    
    from glass.sql.q             import exec_write_q
    from glass.gp.prox.sql       import st_near
    from glass.it.shp            import dbtbl_to_shp as db_to_shp
    from glass.gp.prox.bfing.sql import st_buffer
    from glass.gp.gen            import dissolve
    from glass.tbl.grs           import add_table
    
    time_a = dt.datetime.now().replace(microsecond=0)

    NR = row_num(
        osmdb, lnhTbl, where="roads IS NOT NULL",
        api='psql'
    )

    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not NR:
        return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    NB = row_num(
        osmdb, plTbl, where="building IS NOT NULL",
        api='psql'
    )

    time_c = dt.datetime.now().replace(microsecond=0)

    if NB:
        rq = (
            f"(SELECT gid, roads, bf_roads, geometry "
            f"FROM {lnhTbl} WHERE roads IS NOT NULL)"
        )

        # Update column bf_roads with 'lanes' column values
        # lanes number * some distance in meteres (e.g. 3)

        # Update column bf_roads with 'width' column values
        exec_write_q(osmdb, [(
            f"UPDATE {lnhTbl} "
            "SET bf_roads=CAST(round((CAST(lanes AS integer) * 3), 0) AS integer) "
            "WHERE lanes IS NOT NULL AND lanes ~ '^[0-9]+$'"
        ), (
            f"UPDATE {lnhTbl} "
            "SET bf_roads=CAST(round(CAST(width AS numeric), 0) AS integer) "
            "WHERE width IS NOT NULL AND width ~ '^[0-9]+$' AND "
            "CAST(width AS numeric) < 50"
        )], api='psql')
        
        nroads = st_near(
            osmdb, rq, 'geometry',
            f"(SELECT * FROM {plTbl} WHERE building IS NOT NULL)",
            "geometry", "near_roads", intbl_pk="gid",
            until_dist="12", near_col="dist_near"
        )

        time_d = dt.datetime.now().replace(microsecond=0)
            
        exec_write_q(osmdb, [(
            "UPDATE near_roads SET "
            "bf_roads = CAST(round(CAST(dist_near AS numeric), 0) AS integer) "
            "WHERE dist_near >= 1 AND dist_near <= 12"
        ), (
            "UPDATE near_roads SET bf_roads = 99 WHERE dist_near >= 0 AND "
                "dist_near < 1"
        ), (
            "CREATE INDEX near_dist_idx ON near_roads USING gist (geometry)"
        )], api='psql')

        time_e = dt.datetime.now().replace(microsecond=0)
    
    else:
        nroads =  (
            "(SELECT roads, bf_roads, geometry "
            f"FROM {lnhTbl} WHERE roads IS NOT NULL) AS foo"
        )
        
        time_d = None; time_e = None
    
    # Execute Buffer
    bfTbl = st_buffer(
        osmdb, nroads, "bf_roads", "geometry", "bf_roads",
        cols_select="roads", outTblIsFile=None, dissolve="ALL"
    )
    time_f = dt.datetime.now().replace(microsecond=0)
    
    # Send data to GRASS GIS
    rdv = db_to_shp(
        osmdb, bfTbl, "geometry", "froads", notTable=None,
        filterByReg=True, inDB="psql", outShpIsGRASS=True
    )

    # Dissolve
    drdv = dissolve(rdv, "droads", "roads", api="grass")

    add_table(drdv, None, lyrN=1, asCMD=True)
    
    time_g = dt.datetime.now().replace(microsecond=0)
    
    if asRst:
        from glass.dtt.torst import grsshp_to_grsrst as shp_to_rst
        
        drdv = shp_to_rst(drdv, int(asRst), "rst_roads", cmd=True)
        
        time_h = dt.datetime.now().replace(microsecond=0)
    else:
        time_h = None
    
    return drdv, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('count_rows_build', time_c - time_b),
        2 : None if not time_d else ('near_analysis', time_d - time_c),
        3 : None if not time_e else ('update_buffer_tbl', time_e - time_d),
        4 : ('buffer_roads', time_f - time_e if time_e else time_f - time_c),
        5 : ('import_roads', time_g - time_f),
        6 : None if not time_h else ('roads_to_raster', time_h - time_g)
    }


def num_roads(osmdata, nom, lineTbl, polyTbl, folder, cellsize, srs, rstTemplate):
    """
    Select Roads and convert To Raster
    """
    
    import os
    import numpy                 as np
    from threading               import Thread
    from glass.rd.rst            import rst_to_array
    from glass.tbl.filter        import sel_by_attr
    from glass.gp.prox.bfing.sql import splite_buffer
    from glass.dtt.torst         import shp_to_rst
    from glass.prop.rst          import rst_geoprop
    from glass.wt.rst            import obj_to_rst
    from glass.prop.sql          import row_num
    
    time_a = dt.datetime.now().replace(microsecond=0)
    NR = row_num(osmdata, lineTbl, where="roads IS NOT NULL", api='sqlite')
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    timeGasto = {0 : ('count_rows_roads', time_b - time_a)}
    
    # Get Roads Buffer
    LULC_CLS = '1221' if nom != "GLOBE_LAND_30" else '801'
    bfShps = []
    def exportAndBuffer():
        time_cc = dt.datetime.now().replace(microsecond=0)
        roadFile = splite_buffer(
            osmdata, lineTbl, "bf_roads", "geometry",
            os.path.join(folder, 'bf_roads.gml'),
            whrClause="roads IS NOT NULL",
            outTblIsFile=True, dissolve=None
        )
        time_c = dt.datetime.now().replace(microsecond=0)
        
        distRst = shp_to_rst(
            roadFile, None, cellsize, -1,
            os.path.join(folder, 'rst_roads.tif'),
            epsg=srs, rst_template=rstTemplate, api="gdal"
        )
        time_d = dt.datetime.now().replace(microsecond=0)
        
        bfShps.append(distRst)
        
        timeGasto[1] = ('buffer_roads', time_c - time_cc)
        timeGasto[2] = ('to_rst_roads', time_d - time_c)
    
    BUILDINGS = []
    def exportBuild():
        time_ee = dt.datetime.now().replace(microsecond=0)
        NB = row_num(
            osmdata, polyTbl, where="building IS NOT NULL", api='sqlite'
        )
        
        time_e = dt.datetime.now().replace(microsecond=0)
        
        timeGasto[3] = ('check_builds', time_e - time_ee)
        
        if not NB:
            return
        
        bShp = sel_by_attr(
            osmdata,
            f"SELECT geometry FROM {polyTbl} WHERE building IS NOT NULL",
            os.path.join(folder, 'road_builds.shp'),
            api_gis='ogr'
        )
        time_f = dt.datetime.now().replace(microsecond=0)
        
        bRst = shp_to_rst(
            bShp, None, cellsize, -1,
            os.path.join(folder, 'road_builds.tif'),
            epsg=srs, rst_template=rstTemplate, api='gdal'
        )
        time_g = dt.datetime.now().replace(microsecond=0)
        
        BUILDINGS.append(bRst)
        
        timeGasto[4] = ('export_builds', time_f - time_e)
        timeGasto[5] = ('builds_to_rst', time_g - time_f)
    
    thrds = [
        Thread(name="build-th", target=exportBuild),
        Thread(name='roads-th', target=exportAndBuffer)
    ]
    
    for t in thrds: t.start()
    for t in thrds: t.join()
    
    if not len(BUILDINGS):
        return {LULC_CLS : bfShps[0]}
    
    time_x = dt.datetime.now().replace(microsecond=0)
    BUILD_ARRAY = rst_to_array(BUILDINGS[0], with_nodata=True)
    rst_array = rst_to_array(bfShps[0], with_nodata=True)
    np.place(rst_array, BUILD_ARRAY==1, 0)

    left, cellx, top, celly = rst_geoprop(rstTemplate)
    gtrans = (left, cellx, 0, top, 0, celly)
        
    newRaster = obj_to_rst(
        rst_array, os.path.join(folder, 'fin_roads.tif'),
        gtrans, srs, noData=-1
    )
    
    time_z = dt.datetime.now().replace(microsecond=0)
    
    timeGasto[6] = ('sanitize_roads', time_z - time_x)
    
    return {int(LULC_CLS) : newRaster}, timeGasto


def pg_num_roads(osmdb, nom, lnhTbl, polyTbl, folder, cellsize, srs, rstT):
    """
    Select, Calculate Buffer distance using POSTGIS, make buffer of roads
    and convert roads to raster
    """
    
    import datetime
    import os
    from glass.prop.sql          import row_num
    from glass.gp.prox.bfing.sql import st_buffer
    from glass.dtt.torst         import shp_to_rst
    
    # There are roads?
    time_a = datetime.datetime.now().replace(microsecond=0)
    NR = row_num(osmdb, lnhTbl, where="roads IS NOT NULL", api='psql')
    time_b = datetime.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    # There are buildings?
    NB = row_num(osmdb, polyTbl, where="building IS NOT NULL", api='psql')
    time_c = datetime.datetime.now().replace(microsecond=0)
    
    if NB:
        from glass.gp.prox.sql import st_near
        from glass.sql.q      import exec_write_q
        
        nroads = st_near(osmdb, (
            "(SELECT gid, roads, bf_roads, geometry FROM {} "
            "WHERE roads IS NOT NULL)"
        ).format(lnhTbl), "geometry", (
            "(SELECT * FROM {} WHERE building IS NOT NULL)"
        ).format(polyTbl), "geometry", "near_roads", until_dist="12",
            near_col="dist_near", intbl_pk="gid"
        )
        time_d = datetime.datetime.now().replace(microsecond=0)
        
        exec_write_q(osmdb, [(
            "UPDATE near_roads SET "
            "bf_roads = CAST(round(CAST(dist_near AS numeric), 0) AS integer) "
            "WHERE dist_near >= 1 AND dist_near <= 12"
        ), "CREATE INDEX near_dist_idx ON near_roads USING gist (geometry)"])
        time_e = datetime.datetime.now().replace(microsecond=0)
    
    else:
        nroads = (
            "(SELECT roads, bf_roads, geometry FROM {} "
            "WHERE roads IS NOT NULL) AS foo"
        ).format(lnhTbl)
        
        time_d = None; time_e=None
    
    # Execute Buffer
    bufferShp = st_buffer(
        osmdb, nroads, "bf_roads", "geometry",
        os.path.join(folder, "bf_roads.shp"),
        cols_select="roads", outTblIsFile=True, dissolve=None
    )
    time_f = datetime.datetime.now().replace(microsecond=0)
    
    # Convert to Raster
    roadsRst = shp_to_rst(
        bufferShp, None, cellsize, 0,
        os.path.join(folder, "rst_roads.tif"), epsg=srs, rst_template=rstT,
        api='gdal'
    )
    time_g = datetime.datetime.now().replace(microsecond=0)
    
    LULC_CLS = '1221' if nom != "GLOBE_LAND_30" else '801'
    
    return {int(LULC_CLS) : roadsRst}, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('count_rows_build', time_c - time_b),
        2 : None if not time_d else ('near_analysis', time_d - time_c),
        3 : None if not time_e else ('update_buffer_tbl', time_e - time_d),
        4 : ('buffer_roads', time_f - time_e if time_e else time_f - time_c),
        5 : ('roads_to_raster', time_g - time_f)
    }

