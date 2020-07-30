"""
Overlay operations
"""


"""
Clip Tools
"""

def clip(inFeat, clipFeat, outFeat, api_gis="grass", clip_by_region=None):
    """
    Clip Analysis
    
    api_gis Options:
    * grass
    * pygrass
    * ogr2ogr
    """
    
    if api_gis == "pygrass":
        from grass.pygrass.modules import Module
        
        if not clip_by_region:
            vclip = Module(
                "v.clip", input=inFeat, clip=clipFeat,
                output=outFeat, overwrite=True, run_=False, quiet=True
            )
        else:
            vclip = Module(
                "v.clip", input=inFeat, output=outFeat, overwrite=True,
                flags='r', run_=False, quiet=True
            )
        
        vclip()
    
    elif api_gis == "grass":
        from glass.pyt import execmd
        
        rcmd = execmd(
            "v.clip input={}{} output={} {}--overwrite --quiet".format(
                inFeat, " clip={}".format(clipFeat) if clipFeat else "",
                outFeat, "-r " if not clipFeat else ""
            )
        )
    
    elif api_gis == 'ogr2ogr':
        from glass.pyt            import execmd
        from glass.pyt.oss        import fprop
        from glass.geo.gt.prop.ff import drv_name

        rcmd = execmd((
            "ogr2ogr -f \"{}\" {} {} -clipsrc {} -clipsrclayer {}"
        ).format(
            drv_name(outFeat), outFeat, inFeat, clipFeat,
            fprop(clipFeat, 'fn')
        ))
    
    else:
        raise ValueError("{} is not available!".format(api_gis))
    
    return outFeat


def clip_shp_by_listshp(inShp, clipLst, outLst):
    """
    Clip shapes using as clipFeatures all SHP in clipShp
    Uses a very fast process with a parallel procedures approach
    
    For now, only works with GRASS GIS
    
    Not Working nice with v.clip because of the database
    """
    
    """
    import copy
    from grass.pygrass.modules import Module, ParallelModuleQueue
    
    op_list = []
    
    clipMod = Module(
        "v.clip", input=inShp, overwrite=True, run_=False, quiet=True
    )
    qq = ParallelModuleQueue(nprocs=5)
    
    for i in range(len(clipLst)):
        new_clip = copy.deepcopy(clipMod)
        
        op_list.append(new_clip)
        
        m = new_clip(clip=clipLst[i], output=outLst[i])
        
        qq.put(m)
    qq.wait()
    """
    
    o = [clip(
        inShp, clipLst[i], outLst[i], api_gis="grass"
    ) for i in range(len(clipLst))]
    
    return outLst


"""
Intersection in the same Feature Class/Table
"""

def line_intersect_to_pnt(inShp, outShp, db=None):
    """
    Get Points where two line features of the same feature class
    intersects.
    """
    
    from glass.pyt.oss     import fprop
    from glass.geo.gt.toshp.db import dbtbl_to_shp
    from glass.sql.db      import create_db
    from glass.geo.gql.to      import shp_to_psql
    from glass.geo.gql.ovly    import line_intersection_pnt
    
    # Create DB if necessary
    if not db:
        db = create_db(fprop(inShp, 'fn', forceLower=True), api='psql')
    
    else:
        from glass.sql.i import db_exists
        
        isDb = db_exists(db)
        
        if not isDb:
            create_db(db, api='psql')
    
    # Send data to DB
    inTbl = shp_to_psql(db, inShp, api="shp2pgsql")
    
    # Get result
    outTbl = line_intersection_pnt(db, inTbl, fprop(
        outShp, 'fn', forceLower=True))
    
    # Export data from DB
    outShp = dbtbl_to_shp(
        db, outTbl, "geom", outShp, inDB='psql',
        tableIsQuery=None, api="pgsql2shp")
    
    return outShp


"""
Union Operations
"""


def union(lyrA, lyrB, outShp, api_gis="grass"):
    """
    Calculates the geometric union of the overlayed polygon layers, i.e.
    the intersection plus the symmetrical difference of layers A and B.
    
    API's Available:
    * saga;
    * grass;
    * pygrass;
    """
    
    if api_gis == "saga":
        from glass.pyt import execmd
        
        rcmd = execmd((
            "saga_cmd shapes_polygons 17 -A {} -B {} -RESULT {} -SPLIT 1"
        ).format(lyrA, lyrB, outShp))
    
    elif api_gis == "pygrass":
        from grass.pygrass.modules import Module
        
        un = Module(
            "v.overlay", ainput=lyrA, atype="area",
            binput=lyrB, btype="area", operator="or",
            output=outShp, overwrite=True, run_=False, quiet=True
        )
        
        un()
    
    elif api_gis == "grass":
        from glass.pyt import execmd
        
        outcmd = execmd((
            "v.overlay ainput={} atype=area binput={} btype=area "
            "operator=or output={} --overwrite --quiet"
        ).format(lyrA, lyrB, outShp))
    
    else:
        raise ValueError("{} is not available!".format(api_gis))
    
    return outShp


def union_for_all_pairs(inputList):
    """
    Calculates the geometric union of the overlayed polygon layers 
    for all pairs in inputList
    
    THis is not a good idea! It is only an example!
    """
    
    import copy
    from grass.pygrass.modules import Module, ParallelModuleQueue
    
    op_list = []
    
    unionTool = Module(
        "v.overlay", atype="area", btype="area", operator="or",
        overwrite=True, run_=False, quiet=True
    )
    
    qq = ParallelModuleQueue(nprocs=5)
    outputs = []
    for lyr_a, lyr_b in inputList:
        new_union = copy.deepcopy(unionTool)
        op_list.append(new_union)
        
        un_result = "{}_{}".format(lyr_a, lyr_b)
        nu = new_union(
            ainput=lyr_a, binput=lyr_b, ouput=un_result
        )
        
        qq.put(nu)
        outputs.append(un_result)
    
    qq.wait()
    
    return outputs


def optimized_union_anls(lyr_a, lyr_b, outShp, ref_boundary,
                         workspace=None, multiProcess=None):
    """
    Optimized Union Analysis
    
    Goal: optimize v.overlay performance for Union operations
    """
    
    import os
    from glass.pyt.oss           import fprop, lst_ff
    from glass.pyt.oss           import cpu_cores
    from glass.geo.gt.sample     import create_fishnet
    from glass.geo.wenv.grs      import run_grass
    from glass.geo.gt.toshp      import eachfeat_to_newshp
    from glass.geo.gt.toshp.mtos import shps_to_shp
    from glass.geo.gt.attr       import split_shp_by_attr
    from glass.geo.gt.torst      import shpext_to_rst
    from glass.geo.gt.prop.ext   import get_ext
    
    if workspace:
        if not os.path.exists(workspace):
            from glass.pyt.oss import mkdir
            
            mkdir(workspace, overwrite=True)
    
    else:
        from glass.pyt.oss import mkdir
        
        workspace = mkdir(os.path.join(
            os.path.dirname(outShp), "union_work"))
    
    # Create Fishnet
    ncpu = cpu_cores()
    if ncpu == 12:
        nrow = 4
        ncol = 3
    elif ncpu == 8:
        nrow = 4
        ncol = 2
    else:
        nrow = 2
        ncol = 2
    
    ext = get_ext(ref_boundary)
    width  = (ext[1] - ext[0]) / ncol
    height = (ext[3] - ext[2]) / nrow
    
    gridShp = create_fishnet(
        ref_boundary, os.path.join(workspace, 'ref_grid.shp'),
        width, height, xy_row_col=None
    )
    
    # Split Fishnet in several files
    cellsShp = eachfeat_to_newshp(gridShp, workspace)
    
    if not multiProcess:
        # INIT GRASS GIS Session
        grsbase = run_grass(workspace, location="grs_loc", srs=ref_boundary)
        
        import grass.script.setup as gsetup
        
        gsetup.init(grsbase, workspace, "grs_loc", 'PERMANENT')
        
        # Add data to GRASS GIS
        from glass.geo.gt.toshp.cff import shp_to_grs
        
        cellsShp   = [shp_to_grs(
            shp, fprop(shp, 'fn'), asCMD=True
        ) for shp in cellsShp]
        
        LYR_A = shp_to_grs(lyr_a, fprop(lyr_a, 'fn'), asCMD=True)
        LYR_B = shp_to_grs(lyr_b, fprop(lyr_b, 'fn'), asCMD=True)
        
        # Clip Layers A and B for each CELL in fishnet
        LYRS_A = [clip(
            LYR_A, cellsShp[x], LYR_A + "_" + str(x), api_gis="grass"
        ) for x in range(len(cellsShp))]; LYRS_B = [clip(
            LYR_B, cellsShp[x], LYR_B + "_" + str(x), api_gis="grass"
        ) for x in range(len(cellsShp))]
        
        # Union SHPS
        UNION_SHP = [union(
            LYRS_A[i], LYRS_B[i], "un_{}".format(i), api_gis="grass"
        ) for i in range(len(cellsShp))]
        
        # Export Data
        from glass.geo.gt.toshp.cff import grs_to_shp
        
        _UNION_SHP = [grs_to_shp(
            shp, os.path.join(workspace, shp + ".shp"), "area"
        ) for shp in UNION_SHP]
    
    else:
        def clip_and_union(la, lb, cell, work, proc, output):
            ref_rst = shpext_to_rst(cell, os.path.join(
                os.path.dirname(cell), fprop(cell, 'fn') + '.tif'
            ), cellsize=10)

            # Start GRASS GIS Session
            loc = "proc_" + str(proc)
            grsbase = run_grass(work, location=loc, srs=ref_rst)
            import grass.script.setup as gsetup
            gsetup.init(grsbase, work, loc, 'PERMANENT')
            
            # Import GRASS GIS modules
            from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
            from glass.geo.gt.prop.feat import feat_count
            
            # Add data to GRASS
            a = shp_to_grs(la, fprop(la, 'fn'), filterByReg=True, asCMD=True)
            b = shp_to_grs(lb, fprop(lb, 'fn'), filterByReg=True, asCMD=True)

            if not feat_count(a, gisApi="grass", work=work, loc=loc):
                return
            
            if not feat_count(b, gisApi="grass", work=work,loc=loc):
                return
            
            # Clip
            a_clip = clip(
                a, None, "{}_clip".format(a), api_gis="grass",
                clip_by_region=True
            )
            b_clip = clip(
                b, None, "{}_clip".format(b), api_gis="grass",
                clip_by_region=True
            )
            
            # Union
            u_shp = union(
                a_clip, b_clip,
                "un_{}".format(fprop(cell, 'fn')), api_gis="grass")
            
            # Export
            o = grs_to_shp(u_shp, output, "area")
        
        import multiprocessing
        
        thrds = [multiprocessing.Process(
            target=clip_and_union, name="th-{}".format(i), args=(
                lyr_a, lyr_b, cellsShp[i],
                os.path.join(workspace, "th_{}".format(i)), i,
                os.path.join(workspace, "uniao_{}.shp".format(i))
            )
        ) for i in range(len(cellsShp))]
        
        for t in thrds:
            t.start()
        
        for t in thrds:
            t.join()
        
        ff_shp = lst_ff(workspace, file_format='.shp')
        _UNION_SHP = []
        for i in range(len(cellsShp)):
            p = os.path.join(
                workspace, "uniao_{}.shp".format(i)
            )

            if p in ff_shp:
                _UNION_SHP.append(p)
            else:
                continue
    
    # Merge all union into the same layer
    MERGED_SHP = shps_to_shp(_UNION_SHP, outShp, api="ogr2ogr")
    
    return MERGED_SHP


def intersection(inShp, intersectShp, outShp, api='geopandas'):
    """
    Intersection between ESRI Shapefile
    
    'API's Available:
    * geopandas
    * saga;
    * pygrass;
    * grass;
    """
    
    if api == 'geopandas':
        import geopandas
    
        from glass.geo.gt.fmshp import shp_to_obj
        from glass.geo.gt.toshp import df_to_shp
    
        dfShp       = shp_to_obj(inShp)
        dfIntersect = shp_to_obj(intersectShp)
    
        res_interse = geopandas.overlay(dfShp, dfIntersect, how='intersection')
    
        df_to_shp(res_interse, outShp)
    
    elif api == 'saga':
        from glass.pyt import execmd
        
        cmdout = execmd((
            "saga_cmd shapes_polygons 14 -A {} -B {} -RESULT {} -SPLIT 1"
        ).format(inShp, intersectShp, outShp))
    
    elif api == 'pygrass':
        from grass.pygrass.modules import Module
        
        clip = Module(
            "v.overlay", ainput=inShp, atype="area",
            binput=intersectShp, btype="area", operator="and",
            output=outShp,  overwrite=True, run_=False, quiet=True
        )
        
        clip()
    
    elif api == 'grass':
        from glass.pyt import execmd

        rcmd = execmd((
            "v.overlay ainput={} atype=area, binput={} btype=area "
            "operator=and output={} --overwrite --quiet"
        ).format(
            inShp, intersectShp, outShp
        ))
        
    else:
        raise ValueError("{} is not available!".format(api))
    
    return outShp


def self_intersection(polygons, output):
    """
    Create a result with the self intersections
    """
    
    from glass.pyt import execmd
    
    cmd = (
        'saga_cmd shapes_polygons 12 -POLYGONS {in_poly} -INTERSECT '
        '{out}'
    ).format(in_poly=polygons, out=output)
    
    outcmd = execmd(cmd)
    
    return output


def erase(inShp, erase_feat, out, splitMultiPart=None, notTbl=None,
          api='pygrass'):
    """
    Difference between two feature classes
    
    API's Available:
    * pygrass;
    * grass;
    * saga;
    """
    
    if api == 'saga':
        """
        Using SAGA GIS
        
        It appears to be very slow
        """
        from glass.pyt import execmd
    
        cmd = (
            'saga_cmd shapes_polygons 15 -A {in_shp} -B {erase_shp} '
            '-RESULT {output} -SPLIT {sp}'
        ).format(
            in_shp=inShp, erase_shp=erase_feat,
            output=out,
            sp='0' if not splitMultiPart else '1'
        )
    
        outcmd = execmd(cmd)
    
    elif api == 'pygrass':
        """
        Use pygrass
        """
        
        from grass.pygrass.modules import Module
        
        erase = Module(
            "v.overlay", ainput=inShp, atype="area",
            binput=erase_feat, btype="area", operator="not",
            output=out, overwrite=True, run_=False, quiet=True,
            flags='t' if notTbl else None
        )
    
        erase()
    
    elif api == 'grass':
        """
        Use GRASS GIS tool via command line
        """
        
        from glass.pyt import execmd
        
        rcmd = execmd((
            "v.overlay ainput={} atype=area binput={} "
            "btype=area operator=not output={} {}"
            "--overwrite --quiet"
        ).format(inShp, erase_feat, out, "" if not notTbl else "-t "))
    
    else:
        raise ValueError('API {} is not available!'.format(api))
    
    return out


def check_shape_diff(SHAPES_TO_COMPARE, OUT_FOLDER, REPORT, DB,
                     GRASS_REGION_TEMPLATE):
    """
    Script to check differences between pairs of Feature Classes
    
    Suponha que temos diversas Feature Classes (FC) e que cada uma delas
    possui um determinado atributo; imagine tambem que,
    considerando todos os pares possiveis entre estas FC,
    se pretende comparar as diferencas na distribuicao dos valores
    desse atributo para cada par.
    
    * Dependencias:
    - GRASS;
    - PostgreSQL;
    - PostGIS.
    """
    
    import datetime
    import os;                  import pandas
    from glass.sql.fm           import q_to_obj
    from glass.dct.to           import db_to_tbl
    from glass.sql.to           import df_to_db
    from glass.geo.gt.toshp.cff import shp_to_shp
    from glass.geo.gt.toshp.db  import dbtbl_to_shp
    from glass.geo.gt.toshp.rst import rst_to_polyg
    from glass.geo.gql.to       import shp_to_psql
    from glass.geo.gql.tomtx    import tbl_to_area_mtx
    from glass.geo.gt.prop.ff   import check_isRaster
    from glass.pyt.oss          import fprop
    from glass.sql.db           import create_db
    from glass.sql.tbl          import tbls_to_tbl
    from glass.sql.to           import q_to_ntbl
    from glass.geo.gql.cln      import fix_geom
    from glass.dct.to           import db_to_tbl
    
    # Check if folder exists, if not create it
    if not os.path.exists(OUT_FOLDER):
        from glass.pyt.oss import mkdir
        mkdir(OUT_FOLDER, overwrite=None)
    else:
        raise ValueError('{} already exists!'.format(OUT_FOLDER))
        
    from glass.geo.wenv.grs import run_grass
        
    gbase = run_grass(
        OUT_FOLDER, grassBIN='grass78', location='shpdif',
        srs=GRASS_REGION_TEMPLATE
    )
        
    import grass.script as grass
    import grass.script.setup as gsetup
        
    gsetup.init(gbase, OUT_FOLDER, 'shpdif', 'PERMANENT')
        
    from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
    from glass.geo.gt.torst     import rst_to_grs
    from glass.geo.gt.tbl.fld   import rn_cols
    
    # Convert to SHAPE if file is Raster
    i = 0
    _SHP_TO_COMPARE = {}
    for s in SHAPES_TO_COMPARE:
        isRaster = check_isRaster(s)
    
        if isRaster:
            # To GRASS
            rstName = fprop(s, 'fn')
            inRst   = rst_to_grs(s, "rst_" + rstName, as_cmd=True)
            # To Vector
            d       = rst_to_polyg(inRst, rstName,
                rstColumn="lulc_{}".format(i), gisApi="grass")
                
            # Export Shapefile
            shp = grs_to_shp(
                d, os.path.join(OUT_FOLDER, d + '.shp'), "area")
                
            _SHP_TO_COMPARE[shp] = "lulc_{}".format(i)
    
        else:
            # To GRASS
            grsV = shp_to_grs(s, fprop(s, 'fn'), asCMD=True)
                
            # Change name of column with comparing value
            ncol = "lulc_{}".format(str(i))
            rn_cols(grsV, {
                SHAPES_TO_COMPARE[s] : "lulc_{}".format(str(i))
            }, api="grass")
                
            # Export
            shp = grs_to_shp(
                grsV, os.path.join(OUT_FOLDER, grsV + '_rn.shp'), "area")
                
            _SHP_TO_COMPARE[shp] = "lulc_{}".format(str(i))
        
        i += 1
    
    SHAPES_TO_COMPARE = _SHP_TO_COMPARE
    __SHAPES_TO_COMPARE = SHAPES_TO_COMPARE
    
    # Create database
    create_db(DB, api='psql')
    
    """ Union SHAPEs """
    
    UNION_SHAPE = {}
    FIX_GEOM = {}
    
    SHPS = list(__SHAPES_TO_COMPARE.keys())
    for i in range(len(SHPS)):
        for e in range(i + 1, len(SHPS)):
            # Optimized Union
            print("Union between {} and {}".format(SHPS[i], SHPS[e]))
            time_a = datetime.datetime.now().replace(microsecond=0)
            __unShp = optimized_union_anls(
                SHPS[i], SHPS[e],
                os.path.join(OUT_FOLDER, "un_{}_{}.shp".format(i, e)),
                GRASS_REGION_TEMPLATE,
                os.path.join(OUT_FOLDER, "work_{}_{}".format(i, e)),
                multiProcess=True
            )
            time_b = datetime.datetime.now().replace(microsecond=0)
            print(time_b - time_a)
                
            # Rename cols
            unShp = rn_cols(__unShp, {
                "a_" + __SHAPES_TO_COMPARE[SHPS[i]] : __SHAPES_TO_COMPARE[SHPS[i]],
                "b_" + __SHAPES_TO_COMPARE[SHPS[e]] : __SHAPES_TO_COMPARE[SHPS[e]]
            })
            
            UNION_SHAPE[(SHPS[i], SHPS[e])] = unShp
    
    # Send data to postgresql
    SYNTH_TBL = {}
    
    for uShp in UNION_SHAPE:
        # Send data to PostgreSQL
        union_tbl = shp_to_psql(DB, UNION_SHAPE[uShp], api='shp2pgsql')
        
        # Produce table with % of area equal in both maps
        areaMapTbl = q_to_ntbl(DB, "{}_syn".format(union_tbl), (
            "SELECT CAST('{lulc_1}' AS text) AS lulc_1, "
            "CAST('{lulc_2}' AS text) AS lulc_2, "
            "round("
                "CAST(SUM(g_area) / 1000000 AS numeric), 4"
            ") AS agree_area, round("
                "CAST((SUM(g_area) / MIN(total_area)) * 100 AS numeric), 4"
            ") AS agree_percentage, "
            "round("
                "CAST(MIN(total_area) / 1000000 AS numeric), 4"
            ") AS total_area FROM ("
                "SELECT {map1_cls}, {map2_cls}, ST_Area(geom) AS g_area, "
                "CASE "
                    "WHEN {map1_cls} = {map2_cls} "
                    "THEN 1 ELSE 0 "
                "END AS isthesame, total_area FROM {tbl}, ("
                    "SELECT SUM(ST_Area(geom)) AS total_area FROM {tbl}"
                ") AS foo2"
            ") AS foo WHERE isthesame = 1 "
            "GROUP BY isthesame"
        ).format(
            lulc_1 = fprop(uShp[0], 'fn'), lulc_2 = fprop(uShp[1], 'fn'),
            map1_cls = __SHAPES_TO_COMPARE[uShp[0]],
            map2_cls = __SHAPES_TO_COMPARE[uShp[1]],
            tbl = union_tbl
        ), api='psql')
        
        # Produce confusion matrix for the pair in comparison
        matrixTbl = tbl_to_area_mtx(
            DB, union_tbl,
            __SHAPES_TO_COMPARE[uShp[0]],
            __SHAPES_TO_COMPARE[uShp[1]],
            union_tbl + '_mtx'
        )
        
        SYNTH_TBL[uShp] = {"TOTAL" : areaMapTbl, "MATRIX" : matrixTbl}
    
    # UNION ALL TOTAL TABLES
    total_table = tbls_to_tbl(
        DB, [SYNTH_TBL[k]["TOTAL"] for k in SYNTH_TBL], 'total_table'
    )
    
    # Create table with % of agreement between each pair of maps
    mapsNames = q_to_obj(DB, (
        "SELECT lulc FROM ("
            "SELECT lulc_1 AS lulc FROM {tbl} GROUP BY lulc_1 "
            "UNION ALL "
            "SELECT lulc_2 AS lulc FROM {tbl} GROUP BY lulc_2"
        ") AS lu GROUP BY lulc ORDER BY lulc"
    ).format(tbl=total_table), db_api='psql').lulc.tolist()
    
    FLDS_TO_PIVOT = ["agree_percentage", "total_area"]
    
    Q = (
        "SELECT * FROM crosstab('"
            "SELECT CASE "
                "WHEN foo.lulc_1 IS NOT NULL THEN foo.lulc_1 ELSE jtbl.tmp1 "
            "END AS lulc_1, CASE "
                "WHEN foo.lulc_2 IS NOT NULL THEN foo.lulc_2 ELSE jtbl.tmp2 "
            "END AS lulc_2, CASE "
                "WHEN foo.{valCol} IS NOT NULL THEN foo.{valCol} ELSE 0 "
            "END AS agree_percentage FROM ("
                "SELECT lulc_1, lulc_2, {valCol} FROM {tbl} UNION ALL "
                "SELECT lulc_1, lulc_2, {valCol} FROM ("
                    "SELECT lulc_1 AS lulc_2, lulc_2 AS lulc_1, {valCol} "
                    "FROM {tbl}"
                ") AS tst"
            ") AS foo FULL JOIN ("
                "SELECT lulc_1 AS tmp1, lulc_2 AS tmp2 FROM ("
                    "SELECT lulc_1 AS lulc_1 FROM {tbl} GROUP BY lulc_1 "
                    "UNION ALL "
                    "SELECT lulc_2 AS lulc_1 FROM {tbl} GROUP BY lulc_2"
                ") AS tst_1, ("
                    "SELECT lulc_1 AS lulc_2 FROM {tbl} GROUP BY lulc_1 "
                    "UNION ALL "
                    "SELECT lulc_2 AS lulc_2 FROM {tbl} GROUP BY lulc_2"
                ") AS tst_2 WHERE lulc_1 = lulc_2 GROUP BY lulc_1, lulc_2"
            ") AS jtbl ON foo.lulc_1 = jtbl.tmp1 AND foo.lulc_2 = jtbl.tmp2 "
            "ORDER BY lulc_1, lulc_2"
        "') AS ct("
            "lulc_map text, {crossCols}"
        ")"
    )
    
    TOTAL_AGREE_TABLE = None
    TOTAL_AREA_TABLE  = None
    for f in FLDS_TO_PIVOT:
        if not TOTAL_AGREE_TABLE:
            TOTAL_AGREE_TABLE = q_to_ntbl(DB, "agreement_table", Q.format(
                tbl = total_table, valCol=f,
                crossCols = ", ".join([
                    "{} numeric".format(map_) for map_ in mapsNames])
            ), api='psql')
        
        else:
            TOTAL_AREA_TABLE = q_to_ntbl(DB, "area_table", Q.format(
                tbl = total_table, valCol=f,
                crossCols = ", ".join([
                    "{} numeric".format(map_) for map_ in mapsNames])
            ), api='psql')
    
    # Union Mapping
    UNION_MAPPING = pandas.DataFrame([[
        k[0], k[1], fprop(UNION_SHAPE[k], 'fn')] for k in UNION_SHAPE],
        columns=['shp_a', 'shp_b', 'union_shp']
    )
    
    UNION_MAPPING = df_to_db(DB, UNION_MAPPING, 'union_map', api='psql')
    
    # Export Results
    TABLES = [UNION_MAPPING, TOTAL_AGREE_TABLE, TOTAL_AREA_TABLE] + [
        SYNTH_TBL[x]["MATRIX"] for x in SYNTH_TBL
    ]
    
    SHEETS = ["union_map", "agreement_percentage", "area_with_data_km"] + [
        "{}_{}".format(
            fprop(x[0], 'fn')[:15], fprop(x[1], 'fn')[:15]
        ) for x in SYNTH_TBL
    ]
    
    db_to_tbl(
        DB, ["SELECT * FROM {}".format(x) for x in TABLES],
        REPORT, sheetsNames=SHEETS, dbAPI='psql'
    )
    
    return REPORT


def shp_diff_fm_ref(refshp, refcol, shps, out_folder,
    refrst, db=None):
    """
    Check differences between each shp in shps and one reference shape

    Dependencies:
    - GRASS;
    - PostgreSQL with Postgis or GeoPandas;
    """

    import os
    from glass.geo.gt.prop.ff   import check_isRaster
    from glass.geo.wenv.grs     import run_grass
    from glass.pyt.oss          import fprop
    from glass.geo.gt.tbl.tomtx import tbl_to_areamtx

    # Check if folder exists, if not create it
    if not os.path.exists(out_folder):
        from glass.pyt.oss import mkdir
        mkdir (out_folder)
    
    # Start GRASS GIS Session
    gbase = run_grass(
        out_folder, grassBIN='grass78', location='shpdif',
        srs=refrst
    )

    import grass.script.setup as gsetup

    gsetup.init(gbase, out_folder, 'shpdif', 'PERMANENT')

    from glass.geo.gt.toshp.cff import shp_to_grs, grs_to_shp
    from glass.geo.gt.torst     import rst_to_grs
    from glass.geo.gt.tbl.fld   import rn_cols
    from glass.geo.gt.toshp.rst import rst_to_polyg

    # Convert to SHAPE if file is Raster
    # Rename interest columns
    i = 0
    lstff = [refshp] + list(shps.keys())
    __shps = {}
    for s in lstff:
        is_rst = check_isRaster(s)

        if is_rst:
            # To GRASS
            rname = fprop(s, 'fn')
            inrst = rst_to_grs(s, "rst_" + rname, as_cmd=True)

            # To vector
            d = rst_to_polyg(
                inrst, rname,
                rstColumn="lulc_{}".format(str(i)), gisApi="grass"
            )
        
        else:
            # To GRASS
            d = shp_to_grs(s, fprop(s, 'fn'), asCMD=True)

            # Change name of interest colum
            rn_cols(d, {
                shps[s] if i else refcol : "lulc_{}".format(str(i))
            }, api="grass")

        # Export To Shapefile
        if not i:
            refshp = grs_to_shp(d, os.path.join(out_folder, d + '.shp'), 'area')
            refcol = "lulc_{}".format(str(i))
        
        else:
            shp = grs_to_shp(d, os.path.join(out_folder, d + '.shp'), 'area')
            __shps[shp] = "lulc_{}".format(str(i))
        
        i += 1
    
    # Union Shapefiles
    union_shape = {}

    for shp in __shps:
        # Optimized Union
        sname = fprop(shp, 'fn')
        union_shape[shp] = optimized_union_anls(
            shp, refshp,
            os.path.join(out_folder, sname + '_un.shp'),
            refrst,
            os.path.join(out_folder, "wk_" + sname), multiProcess=True
        )
        
        # Produce confusion matrices
        mtxf = tbl_to_areamtx(
            union_shape[shp], "a_" + __shps[shp], 'b_' + refcol,
            os.path.join(out_folder, sname + '.xlsx'),
            db=db, with_metrics=True
        )

    return out_folder

"""
Indicators from geometries relationships
"""

def count_geom_inside_polygon(count_geom, polygons, outfile,
    count_geom_col='cgeom', pop_col=None, geombypop=None):
    """
    Count the number of geometries inside each polygon.

    The user can also give a population field. The method will return the number
    of geometries by person * 1000.

    E.g. Count the number of points (health care centers, sports) by 
    statistical unit;
    E.g. Count the number of points by inhabitants in each statistical unit.
    """

    from shapely.wkt           import loads
    from glass.geo.gt.fmshp    import shp_to_obj
    from glass.geo.gt.toshp    import obj_to_shp
    from glass.geo.gt.prop.prj import get_epsg_shp

    pnt_df = shp_to_obj(count_geom)
    pol_df = shp_to_obj(polygons)

    count_geom_col = 'cgeom' if not count_geom_col else count_geom_col

    def count_points(row):
        g = loads(row.geometry.wkt)
    
        npnt = 0
        for idx, pnt in pnt_df.iterrows():
            pg = loads(pnt.geometry.wkt)
        
            if g.contains(pg) == True:
                npnt += 1
            else:
                continue
    
        row[count_geom_col] = npnt
    
        return row
    
    pol_df = pol_df.apply(lambda x : count_points(x), axis=1)

    if pop_col:
        geombypop = 'cbymil' if not geombypop else geombypop

        pol_df[geombypop] = (pol_df[count_geom_col] / pol_df[pop_col]) * 1000.0
    
    obj_to_shp(pol_df, 'geometry', get_epsg_shp(polygons), outfile)

    return outfile

