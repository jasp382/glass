"""
Not Views
Methods to assist some procedures that will be used in several views
"""

def get_casegeom(rqst, rqst_fid, data_type, ctx=None):
    """
    Process Geometry data in a POST FORM
    """
    
    import os; from osgeo     import ogr
    from weapi                import DATA_FOLDER
    from gasp3.gt.prj         import get_trans_param
    from gasp3.gt.prop.ext    import get_ext
    from gasp3.gt.prop.prj    import get_epsg
    from gasp3.web.djg.ff.geo import save_geodata
    from gasp3.pyt.oss        import create_folder
    
    if data_type == 'coord' or data_type == 'mapa':
        top    = float(rqst.POST['top-coord{}'.format('' if not ctx else '-b')])
        bottom = float(rqst.POST['bottom-coord{}'.format('' if not ctx else '-b')])
        left   = float(rqst.POST['left-coord{}'.format('' if not ctx else '-b')])
        right  = float(rqst.POST['right-coord{}'.format('' if not ctx else '-b')])
        
        epsg = 4326
    
    else:
        # Get file
        fld = create_folder(os.path.join(DATA_FOLDER, '{}{}'.format(
            "c" if not ctx else "cx", str(rqst_fid))), overwrite=True)
        dataFile = save_geodata(rqst, 
            'shp-{}'.format('a' if not ctx else 'b'), fld)
        
        # Get Extent
        left, right, bottom, top = get_ext(dataFile)
        
        # Get EPSG
        try:
            epsg = get_epsg(dataFile)
        except:
            epsg = None
    
    boundary_points = [(left, top), (right, top), (right, bottom),
                       (left, bottom), (left, top)]
    
    ring = ogr.Geometry(ogr.wkbLinearRing)
    for pnt in boundary_points:
        ring.AddPoint(pnt[0], pnt[1])
    
    geom = ogr.Geometry(ogr.wkbPolygon)
    geom.AddGeometry(ring)
    
    if epsg != 4326:
        geom.Transform(get_trans_param(epsg, 4326))
    
        left, right, bottom, top = geom.GetEnvelope()
    
    geom.FlattenTo2D()
    
    return geom, left, right, bottom, top

#######################################################################
#######################################################################

def get_intervals(dfD, dCols, rqst_id, clrs, N_INT=7, colKEY="COLUMN",
                  method='QUANTILE'):
    import numpy
    from gasp3.pyt.clr import rgb_to_hex
    
    LYR_INTERVALS = []
    e=1
    for obj in dCols:
        if "LYR_FID" not in obj:
            lyr_fid = int(str(rqst_id) + str(e))
            obj["LYR_FID"] = lyr_fid
        
        dfD[obj[colKEY]] = dfD[obj[colKEY]].astype(float)
        
        if method == 'QUANTILE':
            S = 0
            Q = []
        
            for i in range(N_INT-1):
                S += 1/N_INT
                Q.append(S)
        
            INTERVALS = [round(i, 3) for i in dfD[obj[colKEY]].quantile(Q)]
        
        elif method == 'EQUAL_INTERVAL':
            MIN_VAL = dfD[obj[colKEY]].min()
            MAX_VAL = dfD[obj[colKEY]].max()
            
            AMP_INT = (MAX_VAL - MIN_VAL) / 7
            INTERVALS = []
            for i in range(N_INT-1):
                if not i:
                    INTERVALS.append(round(MIN_VAL + AMP_INT, 3))
                else:
                    INTERVALS.append(round(INTERVALS[i-1] + AMP_INT, 3))
        
        for i in range(len(INTERVALS) + 1):
            if not i:
                dfD['{}_int'.format(obj[colKEY])] = numpy.where(
                    dfD[obj[colKEY]] < INTERVALS[i], i+1, 0
                )
            
            elif i == len(INTERVALS):
                dfD['{}_int'.format(obj[colKEY])] = numpy.where(
                    dfD[obj[colKEY]] > INTERVALS[-1], i+1,
                    dfD['{}_int'.format(obj[colKEY])]
                )
            
            else:
                dfD['{}_int'.format(obj[colKEY])] = numpy.where(
                    (dfD[obj[colKEY]] <= INTERVALS[i]) & (dfD[obj[colKEY]] > INTERVALS[i-1]),
                    i+1, dfD['{}_int'.format(obj[colKEY])]
                )
            
            LYR_INTERVALS.append({
                'id_lyr' : obj["LYR_FID"],
                'order'  : i + 1,
                'cat_val': '{} - {}'.format(
                    str(round(dfD[obj[colKEY]].min(), 3)) if not i else str(INTERVALS[i-1]),
                    str(round(dfD[obj[colKEY]].max(), 3)) if i == len(INTERVALS) else str(INTERVALS[i])),
                'color'  : rgb_to_hex(
                    clrs[i]["red"], clrs[i]["green"], clrs[i]["blue"])
            })
            
        # Get Minimum, Maximum and Mean
        if colKEY == "COLUMN":
            obj["MIN"]  = dfD[obj[colKEY]].min()
            obj["MAX"]  = dfD[obj[colKEY]].max()
            obj["MEAN"] = dfD[obj[colKEY]].mean()
        else:
            obj["MIN_CTX"]  = dfD[obj[colKEY]].min()
            obj["MAX_CTX"]  = dfD[obj[colKEY]].max()
            obj["MEAN_CTX"] = dfD[obj[colKEY]].mean()
        
        e+=1
    
    return dCols, LYR_INTERVALS

"""
###############################################################################
############################ Add Layer Utils ##################################
###############################################################################
"""

def add_dt_su(rqst, ctxScaleDif, col_fid, col_fid_ctx, data_cols, TBL_FILE,
              CTX_File, caseFid):
    """
    Add Data for Statistic Unities 
    """
    
    import os;                 import pandas; import numpy
    from gasp3.fm              import tbl_to_obj
    from gasp3.sql.prop           import check_last_id
    from gasp3.sql.fm          import Q_to_df
    from gasp3.sql.to          import df_to_db
    from glass.sql.q     import q_to_ntbl
    from gasp3.pyt.df.mng      import df_cols_to_rows
    from gasp3.web.geosrv.lyrs import pub_pglyr
    from gasp3.web.geosrv.sty  import create_style
    from gasp3.web.geosrv.sty  import assign_style_to_layer
    from gasp3.web.geosrv.sld  import write_sld
    from wgeng.settings        import DATABASES, GEOSERVER_SET
    from weapi.models          import ThemeLyr, StudyCases, Years, LyrIndicators
    
    ###########################################################################
    #################### Queries used along the process #######################
    ###########################################################################
    Q = (
        "SELECT row_number() OVER (ORDER BY aiv.fid) AS fid, "
        "asu.fid AS asu_fid, "
        "aiv.value, asu.design, asu.scale, alyr.lname, alyr.year, "
        "alyr.lunit, CAST(aiv.cls AS text) AS cls, sru.color AS color, "
        "asu.geom AS geom "
        "FROM {} AS aiv "
        "INNER JOIN ("
            "SELECT weapi_lyrindicators.*, "
            "years.year AS year, tlyr.name AS lname, tlyr.unit AS lunit "
            "FROM weapi_lyrindicators "
            "INNER JOIN weapi_years AS years ON weapi_lyrindicators.id_year = years.fid "
            "INNER JOIN weapi_themelyr AS tlyr ON "
                "weapi_lyrindicators.id_indicator = tlyr.fid"
        ") AS alyr ON aiv.id_lyr = alyr.fid "
        "INNER JOIN ("
            "SELECT assu.fid, assu.id_unit, assu.design, assu.geom, "
            "assu.up_unit, assu.up_name, assu.up_tipo, assu.country, "
            "weapi_scale.desig AS scale "
            "FROM weapi_statunit AS assu INNER JOIN weapi_scale "
            "ON assu.scale = weapi_scale.fid"
        ") AS asu ON aiv.id_unit = asu.fid "
        "INNER JOIN weapi_lyrindicatorscls AS sru ON aiv.id_lyr = sru.id_lyr "
            "AND aiv.cls = sru.order "
        "WHERE aiv.id_lyr={}"
    )
    
    Q_SPEC_SU = (
        "SELECT asa.fid AS fid, asu.id_unit AS id_unit "
        "FROM weapi_statcase AS asa "
        "INNER JOIN weapi_statunit AS asu ON "
        "asa.fidunit = asu.fid "
        "WHERE asa.fidcase={} AND ({})"
    )
    ###########################################################################
    ###########################################################################
    
    # Get Case Instance
    case_inst = StudyCases.objects.get(fid=int(caseFid))
    
    DBP = DATABASES['default']
    
    # Get Context Data DataFrame
    ctx_Data = tbl_to_obj(CTX_File)
    
    ctx_Data["whr"] = "asu.id_unit='" + ctx_Data[col_fid_ctx] + "'"
    
    # Get Specific Data Dataframe
    if not ctxScaleDif:
        # Get Statistic Units inside Interest Area
        stat_interest = Q_to_df(DBP, Q_SPEC_SU.format(
            str(caseFid), ctx_Data.whr.str.cat(sep=" OR ")
        ))
        
        data = ctx_Data[ctx_Data[col_fid].isin(stat_interest.id_unit)]
    
    else:
        data = tbl_to_obj(TBL_FILE)
        
        data['whr'] = "asu.id_unit='" + data[col_fid] + "'"
        
        stat_interest = Q_to_df(DBP, Q_SPEC_SU.format(
            str(caseFid), data.whr.str.cat(sep=" OR ")
        ))
        
        data = data[data[col_fid].isin(stat_interest.id_unit)]
    
    # Replace Statistic Unit dicofre for the fid in our database
    stat_units_fid = Q_to_df(DBP, (
        "SELECT asu.fid AS fid, asu.id_unit AS id_unit "
        "FROM weapi_statunit AS asu "
        "WHERE {} OR {}"
    ).format(data.whr.str.cat(sep=" OR "), ctx_Data.whr.str.cat(sep=" OR ")))
    
    data = data.merge(
        stat_units_fid, how='inner',
        left_on=col_fid, right_on='id_unit'
    ); data.drop([col_fid, 'whr', 'id_unit'], axis=1, inplace=True)
    data.rename(columns={'fid' : 'id_unit'}, inplace=True)
    
    ctx_Data = ctx_Data.merge(
        stat_units_fid, how='inner',
        left_on=col_fid_ctx, right_on='id_unit'
    ); ctx_Data.drop([col_fid_ctx, 'whr', 'id_unit'], axis=1, inplace=True)
    ctx_Data.rename(columns={'fid': 'id_unit'}, inplace=True)
    
    # Get Colors for Classes
    ATTR_COLORS = Q_to_df(DBP, (
        "SELECT tbl.red, tbl.blue, tbl.green, (tbl.opacity / 100.0) AS opacity, "
        "tbl.order AS cat, tbl.stk_blue, "
        "tbl.stk_green, tbl.stk_red FROM weapi_sldrules AS tbl "
        "WHERE style=2 ORDER BY tbl.order"
    )).to_dict(orient="records")
    
    # Get Columns Intervals
    data_cols, lyr_int = get_intervals(
        data, data_cols, rqst, ATTR_COLORS, method='EQUAL_INTERVAL'
    ); data_cols, lyr_int_ctx = get_intervals(
        ctx_Data, data_cols, rqst, ATTR_COLORS,
        colKEY="COL_CTX", method='EQUAL_INTERVAL'
    )
    
    # Create layer Intervals Table
    LYR_CLS     = pandas.DataFrame(lyr_int)
    LYR_CLS_CTX = pandas.DataFrame(lyr_int_ctx)
    LYR_CLS['ctx_val'] = LYR_CLS_CTX.cat_val
    LYR_CLS.sort_values(by=['order'], axis=0, inplace=True)
    
    # Columns to Rows Operation
    TO_COLS = {
        # Dict values should have the same length
        'value' : [o["COLUMN"] for o in data_cols],
        'cls'   : [i["COLUMN"] + '_int' for i in data_cols]
    }; TO_COLS_CTX = {
        'value' : [o["COL_CTX"] for o in data_cols],
        'cls'   : [i["COL_CTX"] + '_int' for i in data_cols]
    }
    
    col_old_col_name = 'id_lyr'
    key_old_col_name = 'value'
    
    res = df_cols_to_rows(
        data, TO_COLS, col_old_col_name, key_old_col_name, "id_unit"
    ); res_ctx = df_cols_to_rows(
        ctx_Data, TO_COLS_CTX, col_old_col_name, key_old_col_name,
        'id_unit'
    )
    
    # Replace indicator col name by lyr id
    for obj in data_cols:
        res['id_lyr'] = numpy.where(
            res.id_lyr == obj["COLUMN"], obj["LYR_FID"], res.id_lyr
        ); res_ctx["id_lyr"] = numpy.where(
            res_ctx.id_lyr == obj["COL_CTX"], obj["LYR_FID"], res_ctx.id_lyr
        )
    
    """
    Update Layers Table
    """
    STYLE = 'sty_{}'.format(data_cols[0]['LYR_FID'])
    up_array = []
    for i in range(len(data_cols)):
        li = LyrIndicators.objects.create(
            fid=data_cols[i]["LYR_FID"], id_case=case_inst,
            id_indicator=ThemeLyr.objects.get(fid=int(data_cols[i]["INDICATOR"])),
            id_year=Years.objects.get(fid=int(data_cols[i]["YEAR"])),
            min_val=data_cols[i]["MIN"], max_val=data_cols[i]["MAX"],
            mean_val=data_cols[i]["MEAN"], style=STYLE
        )
    
    """
    Update Indicators Values Table and Layer Classes Table
    """
    # Get last fid in Indicator Values Table & Update fid for new data
    dDf = {'weapi_indvalues' : res, 'weapi_indctxvalues' : res_ctx}
    for t in dDf:
        lastId = check_last_id(DBP, 'fid', t)
        dDf[t]['fid'] = dDf[t].index + lastId + 1
        df_to_db(DBP, dDf[t], t, append=True)
    df_to_db(DBP, LYR_CLS, 'weapi_lyrindicatorscls', append=True)
    
    """
    Setup Layers in Geoserver
    """
    # Write SLD
    SLD = write_sld('cls', ATTR_COLORS, {
        'r' : 'red', 'b' : 'blue', 'g' : 'green', 'category' : 'cat',
        'stroke_r' : 'stk_red', 'stroke_g' : 'stk_green',
        'stroke_b' : 'stk_blue', 'opacity' : 'opacity'
    }, os.path.join(
        os.path.dirname(TBL_FILE), 'sld_{}.sld'.format(data_cols[0]['LYR_FID'])
    ))
    
    # Create Style
    create_style(STYLE, SLD, conf=GEOSERVER_SET, overwrite=True)
    
    for _i in data_cols:
        # Create PSQL View
        nView = q_to_ntbl(
            DBP, 'lyr_{}'.format(_i['LYR_FID']),
            Q.format("weapi_indctxvalues", _i['LYR_FID']), ntblIsView=True
        )
        
        # View for detailed map
        dView = q_to_ntbl(
            DBP, "det_{}".format(_i['LYR_FID']),
            Q.format("weapi_indvalues", _i['LYR_FID']),
            ntblIsView=True)
        
        # Publish New Layers
        L = [nView, dView]
        for l in L:
            pub_pglyr(GEOSERVER_SET["WORKSPACE"], case_inst.slug, l,
                      gs_con=GEOSERVER_SET)
            assign_style_to_layer(STYLE, l, conf=GEOSERVER_SET)
    
    return 304

"""
###############################################################################
###############################################################################
###############################################################################
"""