"""
Overlay operations
"""

import os

from glass.pys      import execmd
from glass.pys.oss  import fprop
from glass.wenv.grs import run_grass

"""
Intersection in the same Feature Class/Table
"""

def line_intersect_to_pnt(inShp, outShp, db=None):
    """
    Get Points where two line features of the same feature class
    intersects.
    """
    
    from glass.it.shp     import dbtbl_to_shp
    from glass.sql.db     import create_db
    from glass.it.db      import shp_to_psql
    from glass.gp.ovl.sql import line_intersection_pnt
    
    # Create DB if necessary
    if not db:
        db = create_db(fprop(inShp, 'fn', forceLower=True), api='psql')
    
    else:
        from glass.prop.sql import db_exists
        
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

def grsunion(lyra, lyrb, oshp, cmd=None):
    """
    GRASS Union
    """

    if cmd:
        outcmd = execmd((
            f"v.overlay ainput={lyra} atype=area "
            f"binput={lyrb} btype=area "
            f"operator=or output={oshp} --overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module
        
        un = Module(
            "v.overlay", ainput=lyra, atype="area",
            binput=lyrb, btype="area", operator="or",
            output=oshp, overwrite=True, run_=False, quiet=True
        )
        
        un()

    return oshp


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
        rcmd = execmd((
            f"saga_cmd shapes_polygons 17 -A {lyrA} "
            f"-B {lyrB} -RESULT {outShp} -SPLIT 1"
        ))
    
    elif api_gis == "pygrass" or api_gis == "grass":
        from glass.prop.prj import get_epsg

        ws = os.path.dirname(outShp)
        refname = fprop(outShp)
        loc = f"loc_{refname}"

        gbase = run_grass(ws, location=loc, srs=get_epsg(lyrA))

        import grass.script.setup as gs

        gs.init(gbase, ws, loc, 'PERMANENT')

        # Import data
        from glass.it.shp import shp_to_grs, grs_to_shp

        lyr_a = shp_to_grs(lyrA, fprop(lyrA, 'fn'), asCMD=True)
        lyr_b = shp_to_grs(lyrB, fprop(lyrB, 'fn'), asCMD=True)

        shpunion = grsunion(
            lyr_a, lyr_b, refname,
            cmd=True if api_gis == "grass" else None
        )

        # Export data
        grs_to_shp(shpunion, outShp, "area")
    
    else:
        raise ValueError(f"{api_gis} is not available!")
    
    return outShp


def union_all(shp_folder, ref, out):
    """
    Union all ESRI Shapefiles in one folder
    """

    from glass.pys.oss import lst_ff

    shps = lst_ff(shp_folder, file_format='.shp')

    # Start GRASS GIS Session
    ws = os.path.dirname(out)
    loc = f'locprod_{fprop(out, "fn")}'

    gb = run_grass(ws, location=loc, srs=ref)

    import grass.script.setup as gsetup

    gsetup.init(gb, ws, loc, 'PERMANENT')

    from glass.it.shp  import shp_to_grs, grs_to_shp
    from glass.tbl.grs import reset_table
    from glass.gp.gen  import dissolve

    res = None
    for shp in shps:
        # Import shapes into grass
        _shp = shp_to_grs(shp)

        if not res:
            res = _shp
            continue
    
        # Union
        res = grsunion(res, _shp, f'un_{_shp}')
    
        # Reset table
        reset_table(res, {'code' : 'integer'}, {'code' : '1'})
    
        # Dissolve
        res = dissolve(res, f'ds_{_shp}', 'code', api='pygrass')
    
    # Export result
    grs_to_shp(res, out, 'area')

    return out


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
        
        un_result = f"{lyr_a}_{lyr_b}"
        nu = new_union(
            ainput=lyr_a, binput=lyr_b,
            ouput=un_result
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
    
    import multiprocessing   as mp
    from glass.pys.oss       import mkdir, fprop, lst_ff
    from glass.pys.oss       import cpu_cores
    from glass.smp           import create_fishnet
    from glass.wenv.grs      import run_grass
    from glass.dtr.split     import eachfeat_to_newshp
    from glass.dtr.mge       import shps_to_shp
    from glass.dtr.ext.torst import shpext_to_rst
    from glass.prop.ext      import get_ext
    
    if workspace:
        if not os.path.exists(workspace):
            mkdir(workspace, overwrite=True)
    
    else:
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
        from glass.it.shp import shp_to_grs
        from glass.gp.ovl.clipp import grsclip
        
        cellsShp   = [shp_to_grs(
            shp, fprop(shp, 'fn'), asCMD=True
        ) for shp in cellsShp]
        
        LYR_A = shp_to_grs(lyr_a, fprop(lyr_a, 'fn'), asCMD=True)
        LYR_B = shp_to_grs(lyr_b, fprop(lyr_b, 'fn'), asCMD=True)
        
        # Clip Layers A and B for each CELL in fishnet
        LYRS_A = [grsclip(
            LYR_A, cellsShp[x], LYR_A + "_" + str(x), cmd=True
        ) for x in range(len(cellsShp))];
        LYRS_B = [grsclip(
            LYR_B, cellsShp[x], LYR_B + "_" + str(x), cmd=True
        ) for x in range(len(cellsShp))]
        
        # Union SHPS
        UNION_SHP = [grsunion(
            LYRS_A[i], LYRS_B[i], f"un_{str(i)}", cmd=True
        ) for i in range(len(cellsShp))]
        
        # Export Data
        from glass.it.shp import grs_to_shp
        
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
            from glass.it.shp import shp_to_grs, grs_to_shp
            from glass.prop.feat import feat_count
            
            # Add data to GRASS
            a = shp_to_grs(la, fprop(la, 'fn'), filterByReg=True, asCMD=True)
            b = shp_to_grs(lb, fprop(lb, 'fn'), filterByReg=True, asCMD=True)

            if not feat_count(a, gisApi="grass", work=work, loc=loc):
                return
            
            if not feat_count(b, gisApi="grass", work=work,loc=loc):
                return
            
            # Clip
            a_clip = grsclip(
                a, None, f"{a}_clip", cmd=True,
                clip_by_region=True
            )
            b_clip = grsclip(
                b, None, f"{b}_clip", cmd=True,
                clip_by_region=True
            )
            
            # Union
            u_shp = grsunion(
                a_clip, b_clip,
                f"un_{fprop(cell, 'fn')}", cmd=True)
            
            # Export
            o = grs_to_shp(u_shp, output, "area")
        
        thrds = [mp.Process(
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


def grsintersection(inshp, intshp, outshp, cmd=None):
    """
    GRASS GIS intersection
    """

    if cmd:
        rcmd = execmd((
            f"v.overlay ainput={inshp} atype=area, "
            f"binput={intshp} btype=area "
            f"operator=and output={outshp} --overwrite --quiet"
        ))
    
    else:
        from grass.pygrass.modules import Module
        
        tool = Module(
            "v.overlay", ainput=inshp, atype="area",
            binput=intshp, btype="area", operator="and",
            output=outshp,  overwrite=True, run_=False, quiet=True
        )
        
        tool()
    
    return outshp


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
    
        from glass.rd.shp import shp_to_obj
        from glass.wt.shp import df_to_shp
    
        dfShp       = shp_to_obj(inShp)
        dfIntersect = shp_to_obj(intersectShp)
    
        res_interse = geopandas.overlay(dfShp, dfIntersect, how='intersection')
    
        df_to_shp(res_interse, outShp)
    
    elif api == 'saga':
        cmdout = execmd((
            f"saga_cmd shapes_polygons 14 -A {inShp} "
            f"-B {intersectShp} -RESULT {outShp} -SPLIT 1"
        ))
    
    elif api == 'pygrass' or api == 'grass':
        from glass.prop.prj import get_epsg

        epsg = get_epsg(inShp)

        w   = os.path.dirname(outShp)
        refname = fprop(outShp, 'fn')
        loc = f"loc_{refname}"

        grsbase = run_grass(w, location=loc, srs=epsg)

        import grass.script.setup as gsetup

        gsetup.init(grsbase, w, loc, 'PERMANENT')

        from glass.it.shp import shp_to_grs, grs_to_shp

        shpa = shp_to_grs(inShp, fprop(inShp, 'fn'))
        shpb = shp_to_grs(intersectShp, fprop(intersectShp, 'fn'))

        # Intersection
        intshp = grsintersection(shpa, shpb, refname,
            True if api == 'grass' else None
        )

        # Export
        r = grs_to_shp(intshp, outShp, 'area')
        
    else:
        raise ValueError(f"{api} is not available!")
    
    return outShp


def count_pntinpol(inpnt, inpoly, cntcol, out):
    """
    Count points inside polygons
    """

    from glass.gp.ovl.obj import count_pnt_inside_poly
    from glass.rd.shp     import shp_to_obj
    from glass.wt.shp     import obj_to_shp
    from glass.prop.prj   import get_shp_epsg

    # Open data
    pnt_df = shp_to_obj(inpnt)
    pol_df = shp_to_obj(inpoly)

    # Count points
    pol_df = count_pnt_inside_poly(pnt_df, cntcol, pol_df)

    # Export to file
    obj_to_shp(pol_df, "geometry", get_shp_epsg(inpoly), out)

    return out


def self_intersection(polygons, output):
    """
    Create a result with the self intersections
    """
    
    cmd = (
        f'saga_cmd shapes_polygons 12 -POLYGONS '
        f'{polygons} -INTERSECT {output}'
    )
    
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

        sp = '0' if not splitMultiPart else '1'
    
        cmd = (
            f'saga_cmd shapes_polygons 15 -A {inShp} -B {erase_feat} '
            f'-RESULT {out} -SPLIT {sp}'
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
            flags='t' if notTbl else ''
        )
    
        erase()
    
    elif api == 'grass':
        """
        Use GRASS GIS tool via command line
        """

        istbl = "" if not notTbl else "-t "
        
        rcmd = execmd((
            f"v.overlay ainput={inShp} atype=area "
            f"binput={erase_feat} btype=area "
            f"operator=not output={out} {istbl}"
            "--overwrite --quiet"
        ))
    
    else:
        raise ValueError(f'API {api} is not available!')
    
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
    import pandas
    from glass.sql.q         import q_to_obj
    from glass.it            import db_to_tbl
    from glass.wt.sql        import df_to_db
    from glass.dtr.rst.toshp import rst_to_polyg
    from glass.it.db         import shp_to_psql
    from glass.dtr.tomtx.sql import tbl_to_area_mtx
    from glass.prop          import is_rst
    from glass.sql.db        import create_db
    from glass.sql.tbl       import tbls_to_tbl
    from glass.sql.q         import q_to_ntbl
    
    # Check if folder exists, if not create it
    if not os.path.exists(OUT_FOLDER):
        from glass.pys.oss import mkdir
        mkdir(OUT_FOLDER, overwrite=None)
    else:
        raise ValueError(f'{OUT_FOLDER} already exists!')
        
    from glass.wenv.grs import run_grass
        
    gbase = run_grass(
        OUT_FOLDER, grassBIN='grass78', location='shpdif',
        srs=GRASS_REGION_TEMPLATE
    )
    
    import grass.script.setup as gsetup
        
    gsetup.init(gbase, OUT_FOLDER, 'shpdif', 'PERMANENT')
        
    from glass.it.shp  import shp_to_grs, grs_to_shp
    from glass.it.rst  import rst_to_grs
    from glass.tbl.col import rn_cols
    
    # Convert to SHAPE if file is Raster
    i = 0
    _SHP_TO_COMPARE = {}
    for s in SHAPES_TO_COMPARE:
        isRaster = is_rst(s)

        ncol = f"lulc_{str(i)}"
    
        if isRaster:
            # To GRASS
            rstName = fprop(s, 'fn')
            inRst   = rst_to_grs(s, f"rst_{rstName}", as_cmd=True)
            # To Vector
            d = rst_to_polyg(
                inRst, rstName,
                rstColumn=ncol, gisApi="grass"
            )
                
            # Export Shapefile
            shp = grs_to_shp(
                d, os.path.join(OUT_FOLDER, f"{d}.shp"), "area")
                
            _SHP_TO_COMPARE[shp] = ncol
    
        else:
            # To GRASS
            grsV = shp_to_grs(s, fprop(s, 'fn'), asCMD=True)
                
            # Change name of column with comparing value
            rn_cols(grsV, {SHAPES_TO_COMPARE[s] : ncol}, api="grass")
                
            # Export
            shp = grs_to_shp(
                grsV, os.path.join(OUT_FOLDER, grsV + '_rn.shp'), "area")
                
            _SHP_TO_COMPARE[shp] = ncol
        
        i += 1
    
    SHAPES_TO_COMPARE   = _SHP_TO_COMPARE
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
                os.path.join(OUT_FOLDER, f"un_{str(i)}_{str(e)}.shp"),
                GRASS_REGION_TEMPLATE,
                os.path.join(OUT_FOLDER, f"work_{str(i)}_{str(e)}"),
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
        areaMapTbl = q_to_ntbl(DB, f"{union_tbl}_syn", (
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

    from glass.prop      import is_rst
    from glass.dtr.tomtx import tbl_to_areamtx

    # Check if folder exists, if not create it
    if not os.path.exists(out_folder):
        from glass.pys.oss import mkdir
        mkdir (out_folder)
    
    # Start GRASS GIS Session
    gbase = run_grass(
        out_folder, grassBIN='grass78', location='shpdif',
        srs=refrst
    )

    import grass.script.setup as gsetup

    gsetup.init(gbase, out_folder, 'shpdif', 'PERMANENT')

    from glass.it.shp        import shp_to_grs, grs_to_shp
    from glass.it.rst        import rst_to_grs
    from glass.tbl.col       import rn_cols
    from glass.dtr.rst.toshp import rst_to_polyg

    # Convert to SHAPE if file is Raster
    # Rename interest columns
    i = 0
    lstff = [refshp] + list(shps.keys())
    __shps = {}
    for s in lstff:
        isrst = is_rst(s)

        if isrst:
            # To GRASS
            rname = fprop(s, 'fn')
            inrst = rst_to_grs(s, f"rst_{rname}", as_cmd=True)

            # To vector
            d = rst_to_polyg(
                inrst, rname,
                rstColumn=f"lulc_{str(i)}", gisApi="grass"
            )
        
        else:
            # To GRASS
            d = shp_to_grs(s, fprop(s, 'fn'), asCMD=True)

            # Change name of interest colum
            rn_cols(d, {
                shps[s] if i else refcol : f"lulc_{str(i)}"
            }, api="grass")

        # Export To Shapefile
        if not i:
            refshp = grs_to_shp(d, os.path.join(out_folder, f"{d}.shp"), 'area')
            refcol = f"lulc_{str(i)}"
        
        else:
            shp = grs_to_shp(d, os.path.join(out_folder, f"{d}.shp"), 'area')
            __shps[shp] = f"lulc_{str(i)}"
        
        i += 1
    
    # Union Shapefiles
    union_shape = {}

    for shp in __shps:
        # Optimized Union
        sname = fprop(shp, 'fn')
        union_shape[shp] = optimized_union_anls(
            shp, refshp,
            os.path.join(out_folder, f"{sname}_un.shp"),
            refrst,
            os.path.join(out_folder, f"wk_{sname}"), multiProcess=True
        )
        
        # Produce confusion matrices
        mtxf = tbl_to_areamtx(
            union_shape[shp], f"a_{__shps[shp]}", f'b_{refcol}',
            os.path.join(out_folder, sname + '.xlsx'),
            db=db, with_metrics=True
        )

    return out_folder
