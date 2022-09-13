from django.http                  import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

"""
Manage Layers Related with Cases
"""

@csrf_exempt
def receive_data(request):
    """
    Receive data
    """
    
    if request.method == 'POST':
        import os
        from atlas                import DATA_FOLDER
        from weapi.models         import StudyCases, UploadData, UploadCols
        from weapi.utils          import get_rqst_id
        from gasp3.web.djg.ff.geo import save_geodata
        from gasp3.pyt.oss        import create_folder
        from gasp3.fm             import tbl_to_obj
        
        # Get Request ID
        rqst_id = get_rqst_id(request)
        
        # Get Study Case
        study_case = request.POST['study-case']
        
        # Get Geom Type
        geom_type  = request.POST['list-geom']
        
        # Get Data Type
        data_type  = request.POST['list-type']
        
        # Context Map Scale
        # Options: "a_mesma" | "m_peq"
        scale_Option = request.POST['list-scale']
        DIF_CTX = True if scale_Option == 'm_peq' else None
        
        # Get File
        outFld   = create_folder(os.path.join(DATA_FOLDER, str(rqst_id)))
        dataFile = save_geodata(request, 'data-file', outFld)
        if DIF_CTX:
            ctxFile  = save_geodata(request, 'scale-data-file', outFld)
        else:
            ctxFile  = None
        
        # Get columns in file or files
        cols = tbl_to_obj(dataFile).columns.values
        if DIF_CTX:
            cols_CTX = tbl_to_obj(ctxFile).columns.values
        else: cols_CTX = None
        
        # Sava data in database
        # Update data table
        case_inst = StudyCases.objects.get(slug=study_case)
        updata_inst = UploadData.objects.create(
            fid=rqst_id, filename=os.path.basename(dataFile),
            utiliza=1, case=case_inst,
            ctx_name=None if not DIF_CTX else os.path.basename(ctxFile)
        )
        
        # Update Columns name table
        for idx in range(len(cols)):
            coli = UploadCols.objects.create(
                fid=int("{}{}".format(str(rqst_id), str(idx))),
                rqst_id=updata_inst, ixd_col=idx, name_col=cols[idx],
                ctx_col=False
            )
        
        if DIF_CTX:
            for idx in range(len(cols_CTX)):
                colix = UploadCols.objects.create(
                    fid=int("{}{}".format(str(rqst_id), str(idx+len(cols)))),
                    rqst_id=updata_inst, idx_col=idx,
                    name_col=cols_CTX[idx], ctx_col=True
                )
        
        return HttpResponseRedirect(
            '/pt/atlas/cases/manage/?status=303&rqst={}&ctxdif={}'.format(
                str(rqst_id), 'true' if DIF_CTX else 'false'
            )
        )
    
    else:
        return HttpResponseRedirect('/pt/atlas/cases/manage/')


@csrf_exempt
def data_stat_unit(request):
    """
    Receive info necessary to add data related with Reference Statistic Unities
    """
    
    from django.http import HttpResponseRedirect
    
    if request.method == 'POST':
        import os; from weapi        import DATA_FOLDER
        from weapi.utils             import get_rqst_id
        from weapi.views.cases.tools import add_dt_su
        
        # Get RQST ID
        rqst = request.POST['fid-rqst']
        
        # Get Scale of Context Map
        ctxScaleDif =  True if request.POST['scale-setup'] == 'true' else None
        
        # Get ID Col
        col_fid     = request.POST['col-fid']
        col_fid_ctx = col_fid if not ctxScaleDif else request.POST['col-fid-ctx']
        
        # Get Case Object
        up_inst     = upload_data.objects.get(fid=int(rqst))
        case        = up_inst.case
        
        # Know who much columns with data we have
        N_COLS = request.POST['n_cols']
        data_cols = []
        for i in range(int(N_COLS)-1):
            if 'col-data-{}'.format(str(i+1)) in request.POST \
                and 'col-text-{}'.format(str(i+1)) in request.POST \
                and 'data-year-{}'.format(str(i+1)) in request.POST:
                
                d = {
                    "COLUMN"    : request.POST['col-data-{}'.format(str(i+1))],
                    "INDICATOR" : request.POST['col-text-{}'.format(str(i+1))],
                    "YEAR"      : request.POST['data-year-{}'.format(str(i+1))]
                }
                
                if ctxScaleDif:
                    d["COL_CTX"] = request.POST['col-ctx-data-{}'.format(str(i+1))]
                else:
                    d["COL_CTX"] = request.POST['col-data-{}'.format(str(i+1))]
                
                data_cols.append(d)
        
        # Get Filenames and file paths
        TBL_FILE = os.path.join(DATA_FOLDER, rqst, request.POST['file_name'])
        CTX_File = TBL_FILE if not ctxScaleDif else os.path.join(
            DATA_FOLDER, rqst, up_inst.ctx_name
        )
        
        status = add_dt_su(
            rqst, ctxScaleDif, col_fid, col_fid_ctx, data_cols,
            TBL_FILE, CTX_File, case.fid)
        
        return HttpResponseRedirect(
            '/gui/backoffice/pt/cases/manage/?status={}'.format(str(status)))
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


@csrf_exempt
def add_indicator_nomap(request):
    """
    Receive info necessary to add data related with Reference Statistic Unities
    """
    
    if request.method == 'POST':
        import os; from weapi.utils  import get_rqst_id
        from gasp3.web.djg.ff.geo    import save_geodata
        from gasp3.pyt.oss           import create_folder
        from weapi.models            import StudyCases, ThemeLyr, Years
        from gasp3.pyt.ff.fld        import cols_name
        from weapi                   import DATA_FOLDER
        from weapi.views.cases.tools import add_dt_su
        
        # Get Request ID
        rqst_id = get_rqst_id(request)
        
        # Get Study Case
        study_case = request.POST['study-case']
        
        # Context Map Scale
        # Options: "a_mesma" | "m_peq"
        scale_Option = request.POST['list-scale']
        DIF_CTX = True if scale_Option == 'm_peq' else None
        
        # Get File
        outFld   = create_folder(os.path.join(DATA_FOLDER, str(rqst_id)))
        dataFile = save_geodata(request, 'data-file', outFld)
        if DIF_CTX:
            ctxFile  = save_geodata(request, 'scale-data-file', outFld)
        else:
            ctxFile = None
        
        # Get Case Object
        case_inst = StudyCases.objects.get(slug=study_case)
        
        # Get Columns Name - Columns of Specific and Context must have the same
        # order
        colsN    = cols_name(dataFile, sheetIdx=0)
        colsNctx = colsN if not ctxFile else cols_name(dataFile, sheetIdx=0)
        
        data_cols = []
        for i in range(1, len(colsN)):
            sp_col_n = colsN[i].split('_')
            
            ind_slug = "_".join(sp_col_n[:-1])
            
            ind_fid  = ThemeLyr.objects.get(slug=ind_slug).fid
            year_fid = Years.objects.get(year=int(sp_col_n[-1])).fid
            
            data_cols.append({
                "COLUMN"    : colsN[i],
                "YEAR"      : year_fid,
                "INDICATOR" : ind_fid,
                "COL_CTX"   : colsNctx[i]
            })
        
        status = add_dt_su(
            rqst_id, DIF_CTX, colsN[0], colsNctx[0], data_cols,
            dataFile, ctxFile, case_inst.fid
        )
        
        return HttpResponseRedirect(
            '/gui/backoffice/pt/cases/manage/?status={}'.format(str(status))
        )
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')

@csrf_exempt
def addpntlyr(request):
    """
    Add Point Layer
    """
    
    
    if request.method == 'POST':
        import os;                 import numpy as np
        from weapi                 import DATA_FOLDER
        from weapi.utils           import get_rqst_id
        from wgeng.settings        import DATABASES, GEOSERVER_SET
        from weapi.models          import StudyCases, PntLyr, PntCols
        from gasp3.web.djg.ff      import save_file
        from gasp3.web.djg.ff.geo  import save_geodata
        from gasp3.fm              import tbl_to_obj
        from gasp3.pyt.oss         import create_folder
        from gasp3.pyt.df.mng      import dfcolstorows
        from glass.sql.q           import q_to_ntbl
        from gasp3.sql.to          import df_to_db
        from gasp3.sql.prop           import check_last_id
        from gasp3.web.geosrv.lyrs import pub_pglyr
        
        conDB = DATABASES['default']
        
        # Get Request ID
        lyr_id = get_rqst_id(request)
        
        # Get Study Case
        study_case = request.POST['study-case']
        
        # Layer Name
        lyrName = request.POST['layer-name']
        
        # Get Data
        outFld = create_folder(os.path.join(DATA_FOLDER, str(lyr_id)))
        dataFile = save_geodata(request, 'data-file', outFld)
        
        # Data To DF
        dfGeom = tbl_to_obj(dataFile, srsTo=4326)
        
        # Get Columns Names
        cols = list(dfGeom.columns.values)
        
        # Add fid column
        dfGeom['weapifid'] = dfGeom.index + 1
        
        # Get Df for categorical values
        dfValues = dfGeom.copy()
        dfValues.drop(['geometry'], axis=1, inplace=True)
        
        cols.remove('geometry')
        # Mantain only geometry in dfGeom
        dfGeom.drop(cols, axis=1, inplace=True)
        
        # Prepare cols to send to database
        ColId = check_last_id(conDB, "fid", "weapi_pntcols") + 1
        cols = {i+ColId : cols[i] for i in range(len(cols))}
        
        # Values - Columns to Rows
        dfValues = dfcolstorows(dfValues, 'col', 'data', colFid="weapifid")
        
        # Create Layer
        case = StudyCases.objects.get(slug=study_case)
        lyrI = PntLyr.objects.create(
            fid=lyr_id, name=lyrName, idcase=case,
            icon='/static/jsidejs/img/usericons/barragens_tamega.png'
        )
        
        # Add Columns
        for colid in cols:
            colI = PntCols.objects.create(
                fid=colid, name=cols[colid], lyrid=lyrI)
        
        # Get Geometry FID
        geomID = check_last_id(conDB, "fid", "weapi_pntgeom") + 1
        dfGeom["fid"] = dfGeom.index + geomID
        
        """
        Add Foreign key in data
        """
        for idx, row in dfGeom.iterrows():
            dfValues['geomid'] = np.where(
                dfValues.weapifid == row.weapifid, row.fid,
                0 if not idx else dfValues.geomid
            )
        dfGeom.drop('weapifid', axis=1, inplace=True)
        dfValues.drop('weapifid', axis=1, inplace=True)
        
        # Add Geometry
        dfGeom['lyrid'] = lyr_id
        df_to_db(
            conDB, dfGeom, "weapi_pntgeom", append=True, api='psql',
            epsg=4326, geomType='Point', colGeom="geometry")
        
        # Add Values
        for c in cols:
            dfValues['col'] = np.where(
                dfValues.col == cols[c], c, dfValues.col
            )
        dataID = check_last_id(conDB, "fid", "weapi_pntdata") + 1
        dfValues["fid"] = dfValues.index + dataID
        df_to_db(conDB, dfValues, "weapi_pntdata", append=True, api='psql')
        
        # Create View
        Q = ("INNER JOIN "
            "(SELECT weapi_pntdata.geomid, weapi_pntdata.data AS {colName} "
            "FROM weapi_pntdata INNER JOIN weapi_pntcols "
            "ON weapi_pntdata.col = weapi_pntcols.fid "
            "WHERE weapi_pntcols.name = '{colName}') AS foo{i} "
            "ON weapi_pntgeom.fid = foo{i}.geomid"
        ); MQ = (
            "SELECT weapi_pntgeom.fid, weapi_pntgeom.geom, {colsN} "
            "FROM weapi_pntgeom {ij}"
        ).format(
            colsN=", ".join(["foo{}.{}".format(
                str(cid), cols[cid]) for cid in cols]),
            ij = " ".join([Q.format(
                colName=cols[cid], i=str(cid)
            ) for cid in cols])
        )
        
        tView = q_to_ntbl(conDB, "pnt_{}".format(
            lyr_id), MQ, ntblIsView=True, api='psql')
        
        """
        Setup Geoserver
        """
        pub_pglyr(GEOSERVER_SET["WORKSPACE"], case.slug, tView, gs_con=GEOSERVER_SET)
        
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')
        
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


@csrf_exempt
def addpolylyr(request):
    """
    Add Point Layer
    """
    
    
    if request.method == 'POST':
        import os;                 import numpy as np
        from weapi                 import DATA_FOLDER
        from weapi.utils           import get_rqst_id
        from wgeng.settings        import DATABASES, GEOSERVER_SET
        from weapi.models          import StudyCases, PolygonLyr, PolygonCols
        from gasp3.web.djg.ff      import save_file
        from gasp3.web.djg.ff.geo  import save_geodata
        from gasp3.fm              import tbl_to_obj
        from gasp3.pyt.oss         import create_folder
        from gasp3.pyt.df.mng      import dfcolstorows
        from gasp3.sql.mng.tbl     import q_to_ntbl
        from gasp3.sql.to          import df_to_db
        from gasp3.sql.prop           import check_last_id
        from gasp3.web.geosrv.lyrs import pub_pglyr
        from gasp3.web.geosrv.sty  import assign_style_to_layer
        
        STYLE = 'red_stroke'
        
        conDB = DATABASES['default']
        
        # Get Request ID
        lyr_id = get_rqst_id(request)
        
        # Get Study Case
        study_case = request.POST['study-case']
        
        # Layer Name
        lyrName = request.POST['layer-name']
        
        # Get Data
        outFld = create_folder(os.path.join(DATA_FOLDER, str(lyr_id)))
        dataFile = save_geodata(request, 'data-file', outFld)
        
        # Data To DF
        dfGeom = tbl_to_obj(dataFile, srsTo=3763)
        
        # Style Column
        dfGeom['cls'] = 1
        
        # Get Columns Names
        cols = list(dfGeom.columns.values)
        
        # Add fid column
        dfGeom['weapifid'] = dfGeom.index + 1
        
        # Get Df for categorical values
        dfValues = dfGeom.copy()
        dfValues.drop(['geometry'], axis=1, inplace=True)
        
        cols.remove('geometry')
        # Mantain only geometry in dfGeom
        dfGeom.drop(cols, axis=1, inplace=True)
        
        # Prepare cols to send to database
        ColId = check_last_id(conDB, "fid", "weapi_polygoncols") + 1
        cols = {i+ColId : cols[i] for i in range(len(cols))}
        
        # Values - Columns to Rows
        dfValues = dfcolstorows(dfValues, 'colfid', 'data', colFid="weapifid")
        
        # Create Layer
        case = StudyCases.objects.get(slug=study_case)
        lyrI = PolygonLyr.objects.create(fid=lyr_id, name=lyrName, fidcase=case)
        
        # Add Columns
        for colid in cols:
            colI = PolygonCols.objects.create(
                fid=colid, name=cols[colid], idlyr=lyrI)
        
        # Get Geometry FID
        geomID = check_last_id(conDB, "fid", "weapi_polygongeom") + 1
        dfGeom["fid"] = dfGeom.index + geomID
        
        """
        Add Foreign key in data
        """
        for idx, row in dfGeom.iterrows():
            dfValues['geomfid'] = np.where(
                dfValues.weapifid == row.weapifid, row.fid,
                0 if not idx else dfValues.geomfid
            )
        dfGeom.drop('weapifid', axis=1, inplace=True)
        dfValues.drop('weapifid', axis=1, inplace=True)
        
        # Add Geometry
        dfGeom['idlyr'] = lyr_id
        df_to_db(
            conDB, dfGeom, "weapi_polygongeom", append=True, api='psql',
            epsg=3763, geomType='Polygon', colGeom="geometry")
        
        # Add Values
        for c in cols:
            dfValues['colfid'] = np.where(
                dfValues.colfid == cols[c], c, dfValues.colfid
            )
        dataID = check_last_id(conDB, "fid", "weapi_polygondata") + 1
        dfValues["fid"] = dfValues.index + dataID
        df_to_db(conDB, dfValues, "weapi_polygondata", append=True, api='psql')
        
        # Create View
        Q = ("INNER JOIN "
            "(SELECT weapi_polygondata.geomfid, weapi_polygondata.data AS {colName} "
            "FROM weapi_polygondata INNER JOIN weapi_polygoncols "
            "ON weapi_polygondata.colfid = weapi_polygoncols.fid "
            "WHERE weapi_polygoncols.name = '{colName}') AS foo{i} "
            "ON weapi_polygongeom.fid = foo{i}.geomfid"
        ); MQ = (
            "SELECT weapi_polygongeom.fid, weapi_polygongeom.geom, {colsN} "
            "FROM weapi_polygongeom {ij}"
        ).format(
            colsN=", ".join(["foo{}.{}".format(
                str(cid), cols[cid]) for cid in cols]),
            ij = " ".join([Q.format(
                colName=cols[cid], i=str(cid)
            ) for cid in cols])
        )
        
        tView = q_to_ntbl(conDB, "poly_{}".format(
            lyr_id), MQ, ntblIsView=True, api='psql')
        
        """
        Setup Geoserver
        """
        pub_pglyr(GEOSERVER_SET["WORKSPACE"], case.slug, tView, gs_con=GEOSERVER_SET)
        assign_style_to_layer(STYLE, tView, conf=GEOSERVER_SET)
        
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')
        
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')

