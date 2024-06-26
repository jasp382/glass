"""
Tools to work with Social Network Data
"""

def dsn_data_collection_by_multibuffer(inBuffers, workspace, db, datasource,
                                       keywords=None):
    """
    Extract Digital Social Network Data for each sub-buffer in buffer.
    A sub-buffer is a buffer with a radius equals to the main buffer radius /2
    and with a central point at North, South, East, West, Northeast, Northwest,
    Southwest and Southeast of the main buffer central point.
    
    inBuffers = {
        "lisbon"    : {
            'x'      : -89004.994779, # in meters
            'y'      : -102815.866054, # in meters
            'radius' : 10000,
            'epsg'   : 3763
        },
        "london     : {
            'x'      : -14210.551441, # in meters
            'y'      : 6711542.47559, # in meters
            'radius' : 10000,
            'epsg'   : 3857
        }
    }
    or
    inBuffers = {
        "lisbon" : {
            "path" : /path/to/file.shp,
            "epsg" : 3763
        }
    }
    
    keywords = ['flood', 'accident', 'fire apartment', 'graffiti', 'homeless']
    
    datasource = 'facebook' or datasource = 'flickr'
    TODO: Only works for Flickr and Facebook
    """
    
    import os
    from osgeo               import ogr
    from glass.pys           import obj_to_lst
    from glass.sql.db        import create_pgdb
    from glass.sql.q         import q_to_ntbl
    from glass.wt.sql        import df_to_db
    from glass.it.db         import shp_to_psql
    from glass.it.shp        import dbtbl_to_shp
    from glass.gp.prox.bfing import get_sub_buffers, dic_buffer_array_to_shp
    
    if datasource == 'flickr':
        from glass.acq.dsn.flickr import photos_location
    
    elif datasource == 'facebook':
        from glass.acq.dsn.fb.places import places_by_query
    
    keywords = obj_to_lst(keywords)
    keywords = ["None"] if not keywords else keywords
    
    # Create Database to Store Data
    create_pgdb(db, overwrite=True, api='psql')
    
    for city in inBuffers:
        # Get Smaller Buffers
        if "path" in inBuffers[city]:
            # Get X, Y and Radius
            from glass.prop.feat.bf import bf_prop
            
            __bfprop = bf_prop(
                inBuffers[city]["path"], inBuffers[city]["epsg"], isFile=True
            )
            
            inBuffers[city]["x"]      = __bfprop["X"]
            inBuffers[city]["y"]      = __bfprop["Y"]
            inBuffers[city]["radius"] = __bfprop["R"]
        
        inBuffers[city]["list_buffer"] = [{
            'X' : inBuffers[city]["x"], 'Y' : inBuffers[city]["y"],
            'RADIUS' : inBuffers[city]['radius'], 'cardeal' : 'major'
        }] + get_sub_buffers(
            inBuffers[city]["x"], inBuffers[city]["y"],
            inBuffers[city]["radius"]
        )
        
        # Smaller Buffers to File
        multiBuffer = os.path.join(workspace, f'buffers_{city}.shp')
        dic_buffer_array_to_shp(
            inBuffers[city]["list_buffer"], multiBuffer,
            inBuffers[city]['epsg'], fields={'cardeal' : ogr.OFTString}
        )
        
        # Retrive data for each keyword and buffer
        # Record these elements in one dataframe
        c       = None
        tblData = None
        for bf in inBuffers[city]["list_buffer"]:
            for k in keywords:
                if datasource == 'flickr':
                    tmpData = photos_location(
                        bf, inBuffers[city]["epsg"],
                        keyword=k if k != 'None' else None,
                        epsg_out=inBuffers[city]["epsg"],
                        onlySearchAreaContained=False
                    )
                
                elif datasource == 'facebook':
                    tmpData = places_by_query(
                        bf, inBuffers[city]["epsg"],
                        keyword=k if k != 'None' else None,
                        epsgOut=inBuffers[city]["epsg"],
                        onlySearchAreaContained=False
                    )
                
                if type(tmpData) == int:
                    print(f"NoData finded for buffer '{bf['cardeal']}' and keyword '{k}'")
                    
                    continue
                
                tmpData["keyword"]   = k
                tmpData["buffer_or"] = bf["cardeal"]
                
                if not c:
                    tblData = tmpData
                    c = 1
                else:
                    tblData = tblData.append(tmpData, ignore_index=True)
        
        inBuffers[city]["data"] = tblData
        
        # Get data columns names
        cols = inBuffers[city]["data"].columns.values
        dataColumns = [
            c for c in cols if c != 'geom' and c != 'keyword' \
            and c != 'buffer_or' and c != 'geometry'
        ]
        
        # Send data to PostgreSQL
        if 'geometry' in cols:
            cgeom = 'geometry'
        
        else:
            cgeom = 'geom'
        
        inBuffers[city]["table"] = f'tbldata_{city}'
        
        df_to_db(
            db, inBuffers[city]["data"],
            inBuffers[city]["table"], api='psql',
            epsg=inBuffers[city]["epsg"],
            geom_type='POINT', col_geom=cgeom
        )
        
        # Send Buffers data to PostgreSQL
        inBuffers[city]["pg_buffer"] = shp_to_psql(
            db, multiBuffer, api="shp2pgsql",
            tnames={multiBuffer : f'buffers_{city}'},
            srs=inBuffers[city]["epsg"]
        )
        
        cols = ', '.join(dataColumns)
        q = (
            "SELECT srcdata.*, "
            "array_agg(buffersg.cardeal ORDER BY buffersg.cardeal) "
            "AS intersect_buffer FROM ("
                f"SELECT {cols}, keyword, geom, "
                "array_agg(buffer_or ORDER BY buffer_or) AS extracted_buffer "
                f"FROM {inBuffers[city]['table']} "
                f"GROUP BY {cols}, keyword, geom"
            ") AS srcdata, ("
                "SELECT cardeal, geom AS bfg "
                f"FROM {inBuffers[city]['pg_buffer']}"
            ") AS buffersg "
            "WHERE ST_Intersects(srcdata.geom, buffersg.bfg) IS TRUE "
            f"GROUP BY {cols}, keyword, geom, extracted_buffer"
        )
        inBuffers[city]["filter_table"] = q_to_ntbl(
            db, f"filter_{inBuffers[city]['table']}", q,
            api='psql'
        )
        
        q = (
            "SELECT * FROM ("
                "SELECT srcdata.*, "
                "array_agg(buffersg.cardeal ORDER BY buffersg.cardeal) "
                "AS not_intersect_buffer FROM ("
                    f"SELECT {cols}, keyword, geom, "
                    "array_agg(buffer_or ORDER BY buffer_or) AS extracted_buffer "
                    f"FROM {inBuffers[city]['table']} "
                    f"GROUP BY {cols}, keyword, geom"
                ") AS srcdata, ("
                    "SELECT cardeal, geom AS bfg "
                    f"FROM {inBuffers[city]['pg_buffer']}"
                ") AS buffersg "
                "WHERE ST_Intersects(srcdata.geom, buffersg.bfg) IS NOT TRUE "
                f"GROUP BY {cols}, keyword, geom, extracted_buffer"
            ") AS foo "
            "WHERE array_length(not_intersect_buffer, 1) = 9"
        )
        inBuffers[city]["outside_table"] = q_to_ntbl(
            db, f"outside_{inBuffers[city]['table']}",
            q, api='psql'
        )
        
        # Union these two tables
        inBuffers[city]["table"] = q_to_ntbl(db, f"data_{city}", (
            "SELECT * "
            f"FROM {inBuffers[city]['filter_table']} "
            "UNION ALL "
            f"SELECT {cols}, keyword, geom, extracted_buffer, "
            "CASE WHEN array_length(not_intersect_buffer, 1) = 9 "
            f"THEN '{'{' + '}'}' ELSE not_intersect_buffer END AS "
            f"intersect_buffer FROM {inBuffers[city]['outside_table']}"
        ), api='psql')
        
        """
        Get Buffers table with info related:
        -> pnt_obtidos = nr pontos obtidos usando esse buffer
        -> pnt_obtidos_fora = nt pontos obtidos fora desse buffer, mas 
        obtidos com ele
        -> pnt_intersect = nt pontos que se intersectam com o buffer
        -> pnt_intersect_non_obtain = nr pontos que se intersectam mas nao 
        foram obtidos como buffer
        """
        inBuffers[city]["pg_buffer"] = q_to_ntbl(
            db, f"dt_{inBuffers[city]['pg_buffer']}", (
                "SELECT main.*, get_obtidos.pnt_obtidos, "
                "obtidos_fora.pnt_obtidos_fora, intersecting.pnt_intersect, "
                "int_not_obtained.pnt_intersect_non_obtain "
                "FROM {bf_table} AS main "
                "LEFT JOIN ("
                    "SELECT gid, cardeal, COUNT(gid) AS pnt_obtidos "
                    "FROM {bf_table} AS bf "
                    "INNER JOIN {dt_table} AS dt "
                    "ON bf.cardeal = ANY(dt.extracted_buffer) "
                    "GROUP BY gid, cardeal"
                ") AS get_obtidos ON main.gid = get_obtidos.gid "
                "LEFT JOIN ("
                    "SELECT gid, cardeal, COUNT(gid) AS pnt_obtidos_fora "
                    "FROM {bf_table} AS bf "
                    "INNER JOIN {dt_table} AS dt "
                    "ON bf.cardeal = ANY(dt.extracted_buffer) "
                    "WHERE ST_Intersects(bf.geom, dt.geom) IS NOT TRUE "
                    "GROUP BY gid, cardeal"
                ") AS obtidos_fora ON main.gid = obtidos_fora.gid "
                "LEFT JOIN ("
                    "SELECT gid, cardeal, COUNT(gid) AS pnt_intersect "
                    "FROM {bf_table} AS bf "
                    "INNER JOIN {dt_table} AS dt "
                    "ON bf.cardeal = ANY(dt.intersect_buffer) "
                    "GROUP BY gid, cardeal"
                ") AS intersecting ON main.gid = intersecting.gid "
                "LEFT JOIN ("
                    "SELECT gid, cardeal, COUNT(gid) AS pnt_intersect_non_obtain "
                    "FROM {bf_table} AS bf "
                    "INNER JOIN {dt_table} AS dt "
                    "ON bf.cardeal = ANY(dt.intersect_buffer) "
                    "WHERE NOT (bf.cardeal = ANY(dt.extracted_buffer)) "
                    "GROUP BY gid, cardeal"
                ") AS int_not_obtained "
                "ON main.gid = int_not_obtained.gid "
                "ORDER BY main.gid"
            ).format(
                bf_table = inBuffers[city]["pg_buffer"],
                dt_table = inBuffers[city]["table"]
            ), api='psql'
        )
        
        """
        Get Points table with info related:
        -> nobtido = n vezes um ponto foi obtido
        -> obtido_e_intersect = n vezes um ponto foi obtido usando um buffer 
        com o qual se intersecta
        -> obtido_sem_intersect = n vezes um ponto foi obtido usando um buffer
        com o qual nao se intersecta
        -> nintersect = n vezes que um ponto se intersecta com um buffer
        -> intersect_sem_obtido = n vezes que um ponto nao foi obtido apesar
        de se intersectar com o buffer
        """
        inBuffers[city]["table"] = q_to_ntbl(
            db, f"info_{city}", (
                "SELECT {cols}, dt.keyword, dt.geom, "
                "CAST(dt.extracted_buffer AS text) AS extracted_buffer, "
                "CAST(dt.intersect_buffer AS text) AS intersect_buffer, "
                "array_length(extracted_buffer, 1) AS nobtido, "
                "SUM(CASE WHEN ST_Intersects(bf.geom, dt.geom) IS TRUE "
                    "THEN 1 ELSE 0 END) AS obtido_e_intersect, "
                "(array_length(extracted_buffer, 1) - SUM("
                    "CASE WHEN ST_Intersects(bf.geom, dt.geom) IS TRUE "
                    "THEN 1 ELSE 0 END)) AS obtido_sem_intersect, "
                "array_length(intersect_buffer, 1) AS nintersect, "
                "(array_length(intersect_buffer, 1) - SUM("
                    "CASE WHEN ST_Intersects(bf.geom, dt.geom) IS TRUE "
                    "THEN 1 ELSE 0 END)) AS intersect_sem_obtido "
                "FROM {dt_table} AS dt "
                "INNER JOIN {bf_table} AS bf "
                "ON bf.cardeal = ANY(dt.extracted_buffer) "
                "GROUP BY {cols}, dt.keyword, dt.geom, "
                "dt.extracted_buffer, dt.intersect_buffer"
            ).format(
                dt_table = inBuffers[city]["table"],
                bf_table = inBuffers[city]["pg_buffer"],
                cols     = ", ".join([f"dt.{x}" for x in dataColumns])
            ), api='psql'
        )
        
        # Export Results
        dbtbl_to_shp(
            db, inBuffers[city]["table"], 'geom',
            os.path.join(workspace, f"{inBuffers[city]['table']}.shp"),
            api='psql', epsg=inBuffers[city]["epsg"]
        )
        
        dbtbl_to_shp(
            db, inBuffers[city]["pg_buffer"], 'geom',
            os.path.join(workspace, f"{inBuffers[city]['pg_buffer']}.shp"),
            api='psql', epsg=inBuffers[city]["epsg"]
        )
    
    return inBuffers


def dsnsearch_by_cell(GRID_PNT, EPSG, RADIUS, DATA_SOURCE, db, OUTPUT_TABLE):
    """
    Search for data in DSN and other platforms by cell
    """
    
    import time;
    from glass.rd.shp            import shp_to_obj
    from glass.sql.db            import create_pgdb
    from glass.acq.dsn.fb.places import places_by_query
    from glass.prj.obj           import df_prj
    from glass.dtt.mge.pd        import merge_df
    from glass.it.shp            import dbtbl_to_shp
    from glass.sql.q             import q_to_ntbl
    from glass.wt.sql            import df_to_db
    
    # Open GRID SHP
    GRID_DF = shp_to_obj(GRID_PNT)
    GRID_DF = df_prj(GRID_DF, 4326) if EPSG != 4326 else GRID_DF
    
    GRID_DF["lng"]     = GRID_DF.geometry.x.astype(float)
    GRID_DF["lat"]     = GRID_DF.geometry.y.astype(float)
    GRID_DF["grid_id"] = GRID_DF.index
    
    # GET DATA
    RESULTS = []
    def get_data(row, datasrc):
        if datasrc == 'facebook':
            d = places_by_query(
                {'x' : row.lng, 'y' : row.lat, 'r' : RADIUS}, 4326,
                keyword=None, epsgOut=EPSG, _limit='100',
                onlySearchAreaContained=None
            )
        
        else:
            raise ValueError(f'{datasrc} as datasource is not a valid value')
        
        if type(d) == int:
            return
        
        d['grid_id'] = row.grid_id
        
        RESULTS.append(d)
        
        time.sleep(5)
    
    GRID_DF.apply(lambda x: get_data(x, DATA_SOURCE), axis=1)
    
    RT = merge_df(RESULTS)
    
    # Create DB
    create_pgdb(db, overwrite=True, api='psql')
    
    # Send Data to PostgreSQL
    df_to_db(
        db, RT, f"{DATA_SOURCE}_data",
        EPSG, "POINT",
        colGeom='geometry' if 'geometry' in RT.columns.values else 'geom'
    )
    
    COLS = [
        x for x in RT.columns.values if x != "geometry" and \
        x != 'geom' and x != "grid_id"
    ] + ["geom"]
    
    GRP_BY_TBL = q_to_ntbl(db, f"{DATA_SOURCE}_grpby", (
        f"SELECT {', '.join(COLS)}, "
        "CAST(array_agg(grid_id) AS text) AS grid_id "
        f"FROM {DATA_SOURCE}_data "
        f"GROUP BY {', '.join(COLS)}"
    ), api='psql')
    
    dbtbl_to_shp(
        db, GRP_BY_TBL, "geom", OUTPUT_TABLE,
        api="psql", epsg=EPSG
    )
    
    return OUTPUT_TABLE

