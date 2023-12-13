def roads_fmdb(osmdb, lnhTbl, plTbl, apidb='SQLITE', asRst=None):
    """
    Raods procedings using SQLITE or PostGIS
    """
    
    import datetime as dt
    from glass.prop.sql import row_num as cnt_rows
    from glass.it.shp   import dbtbl_to_shp as db_to_shp
    if apidb=='SQLITE':
        from glass.gp.prox.bfingsql import splite_buffer as st_buffer
    else:
        from glass.gp.prox.bfingsql import st_buffer
    
    time_a = dt.datetime.now().replace(microsecond=0)
    NR = cnt_rows(osmdb, lnhTbl, where="roads IS NOT NULL",
        api='psql' if apidb == 'POSTGIS' else 'sqlite'
    )
    time_b = dt.datetime.now().replace(microsecond=0)
    
    if not NR: return None, {0 : ('count_rows_roads', time_b - time_a)}
    
    NB = cnt_rows(osmdb, plTbl, where="building IS NOT NULL",
        api='psql' if apidb == 'POSTGIS' else 'sqlite'
    )
    time_c = dt.datetime.now().replace(microsecond=0)
    
    if NB:
        from glass.sql.q       import exec_write_q
        from glass.gp.prox.sql import st_near
        
        ROADS_Q = (
            f"(SELECT{'' if apidb == 'SQLITE' else ' gid,'}"
            " roads, bf_roads, geometry "
            f"FROM {lnhTbl} WHERE roads IS NOT NULL)"
        )

        if apidb == 'SQLITE':
            nroads = st_near(
                osmdb, ROADS_Q, "geometry",
                plTbl, "geometry", "near_roads",
                whrNear="building IS NOT NULL", api='splite',
                near_col='dist_near'
            )
            time_d = dt.datetime.now().replace(microsecond=0)
        
            # Update buffer distance field
            exec_write_q(osmdb, [(
                "UPDATE near_roads SET bf_roads = CAST(round(dist_near, 0) AS integer) "
                "WHERE dist_near >= 1 AND dist_near <= 12"
            ), (
                "UPDATE near_roads SET bf_roads = 1 WHERE dist_near >= 0 AND "
                "dist_near < 1"
            )], api='sqlite')
            time_e = dt.datetime.now().replace(microsecond=0)
        
        else:
            nroads = st_near(
                osmdb, ROADS_Q, 'geometry',
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
                "UPDATE near_roads SET bf_roads = 1 WHERE dist_near >= 0 AND "
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
    roadsGrs = db_to_shp(
        osmdb, bfTbl, "geometry", "froads", notTable=None, filterByReg=True,
        inDB="psql" if apidb == 'POSTGIS' else 'sqlite',
        outShpIsGRASS=True
    )
    time_g = dt.datetime.now().replace(microsecond=0)
    
    if asRst:
        from glass.dtt.rst.torst import grsshp_to_grsrst as shp_to_rst
        
        roadsGrs = shp_to_rst(
            roadsGrs, int(asRst), "rst_roads", cmd=True
        )
        
        time_h = dt.datetime.now().replace(microsecond=0)
    else:
        time_h = None
    
    return roadsGrs, {
        0 : ('count_rows_roads', time_b - time_a),
        1 : ('count_rows_build', time_c - time_b),
        2 : None if not time_d else ('near_analysis', time_d - time_c),
        3 : None if not time_e else ('update_buffer_tbl', time_e - time_d),
        4 : ('buffer_roads', time_f - time_e if time_e else time_f - time_c),
        5 : ('import_roads', time_g - time_f),
        6 : None if not time_h else ('roads_to_raster', time_h - time_g)
    }

