"""
Add Statistic Unities
"""

from django.shortcuts             import render
from django.http                  import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_grpstat(request):
    """
    Get info About Statistic Units Group
    """
    
    if request.method == 'POST':
        import os; from weapi     import DATA_FOLDER
        from weapi.models         import Countries, UploadData, UploadCols
        from weapi.utils          import get_rqst_id
        from gasp3.pyt.oss        import create_folder
        from gasp3.fm             import tbl_to_obj
        from gasp3.gt.prop.feat   import lst_fld
        from gasp3.web.djg.ff.geo import save_geodata
        
        # Get Request ID
        rqst_id = get_rqst_id(request)
        
        # Get data from FORM
        slug      = request.POST['slug']
        descricao = request.POST['descricao']
        
        outFld  = create_folder(os.path.join(DATA_FOLDER, str(rqst_id)))
        shpFile = save_geodata(request, 'shp-file', outFld)
        
        # Get columns in File
        try:
            cols = tbl_to_obj(shpFile).columns.values
        except:
            cols = lst_fld(shpFile)
        
        # Save data in database
        # Update data table
        updata_i = UploadData.objects.create(
            fid=rqst_id, filename=os.path.basename(shpFile), utiliza=1
        )
        
        # Update Columns name table
        for idx in range(len(cols)):
            coli = UploadCols.objects.create(
                fid=int("{}{}".format(str(rqst_id), str(idx))),
                rqst_id=updata_i, idx_col=idx, name_col=cols[idx],
                ctx_col=False
            )
        
        # Update Group Table
        grpsu = Countries.objects.create(
            fid=rqst_id, slug=slug, descricao=descricao)
        
        return HttpResponseRedirect(
            '/gui/backoffice/pt/su/manage/?status=101&rqst={}'.format(
                str(rqst_id)
            )
        )
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/su/manage/')


@csrf_exempt
def add_statgeom(request):
    """
    Add Statistic Units Geometry
    """
    
    if request.method == 'POST':
        import os; import numpy as np
        from shapely.geometry.multipolygon import MultiPolygon
        from weapi                   import DATA_FOLDER
        from weapi.models            import Countries, Scale
        from wgeng.settings          import DATABASES, GEOSERVER_SET
        from gasp3.fm                import tbl_to_obj
        from gasp3.sql.to            import df_to_db
        from gasp3.pyt.df.fld        import col_distinct
        from gasp3.sql.prop             import check_last_id
        from glass.sql.q             import q_to_ntbl
        from gasp3.web.djg.mdl.w     import update_model
        from gasp3.web.geosrv.stores import create_pgstore
        from gasp3.web.geosrv.lyrs   import pub_pglyr
        
        conDB = DATABASES['default']
        
        # Get FORM Data
        rqst          = request.POST['fid-rqst']
        file_name     = request.POST['file-name']
        col_fid       = request.POST['col-fid']
        col_name      = request.POST['col-name']
        col_scale     = request.POST['col-scale']
        col_fid_rel   = request.POST['col-fid-rel']
        col_name_rel  = request.POST['col-name-rel']
        col_scale_rel = request.POST['col-scale-rel']
        
        # Get Country Instance
        cinst = Countries.objects.get(fid=int(rqst))
        
        # File To GEODF
        shpDf = tbl_to_obj(
            os.path.join(DATA_FOLDER, rqst, file_name),
            #geomCol='geometry',
        )
        
        # Get Scales names
        lastScale = check_last_id(conDB, 'fid', 'weapi_scale')
        scales = col_distinct(shpDf, col_scale)
        # Send Scales to DB
        for i in range(len(scales)):
            si = Scale.objects.create(
                fid = lastScale + i,
                desig = scales[i].lower(), id_grp=cinst
            )
            scales[i] = {
                'fid' : lastScale + i, 'desig' : scales[i].lower()
            }
        
        # Replace Scales name by ID
        shpDf[col_scale]     = shpDf[col_scale].str.lower()
        shpDf[col_scale_rel] = shpDf[col_scale_rel].str.lower()
        for s in scales:
            shpDf[col_scale] = np.where(
                shpDf[col_scale] == s['desig'],
                s['fid'], shpDf[col_scale]
            )
            
            shpDf[col_scale_rel] = np.where(
                shpDf[col_scale_rel] == s['desig'],
                s['fid'], shpDf[col_scale_rel]
            )
        
        # Send Geometries to Database
        shpDf.rename(columns={
            col_fid : 'id_unit', col_name : 'design',
            col_scale : 'scale', col_fid_rel : 'up_unit',
            col_name_rel : 'up_name', col_scale_rel: 'up_tipo',
        }, inplace=True)
        shpDf['country'] = rqst
        
        cols = ['id_unit', 'design', 'scale', 'up_unit', 'up_name', 'up_tipo',
                'country', 'geometry']
        delCols = [i for i in shpDf.columns.values if i not in cols]
        shpDf.drop(delCols, axis=1, inplace=True)
        
        # Force MultiPolygon
        def force_multi(geom):
            if geom.geom_type == 'Polygon':
                return MultiPolygon([geom])
            
            else:
                return geom
        
        shpDf["geometry"] = shpDf.geometry.apply(
            lambda x: force_multi(x)
        )
        
        df_to_db(
            conDB, shpDf, 'weapi_statunit', api='psql', epsg=3763,
            geomType='MultiPolygon', colGeom="geometry", append=True
        )
        
        # Create Layers in GeoServer
        create_pgstore(
            cinst.slug, GEOSERVER_SET["WORKSPACE"], conDB, GEOSERVER_SET
        )
        
        for s in scales:
            nView = q_to_ntbl(conDB, "{}_{}".format(
                cinst.slug, s['desig']), (
                "SELECT * FROM weapi_statunit WHERE "
                "country={} AND scale={}"
            ).format(str(rqst), str(s['fid'])), ntblIsView=True)
            
            pub_pglyr(GEOSERVER_SET["WORKSPACE"], cinst.slug, nView, 
                gs_con=GEOSERVER_SET
            )
        
        return HttpResponseRedirect('/gui/backoffice/pt/su/manage/?status=102')
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/su/manage/')


def del_su(request, idgrp):
    """
    Delete Group
    """
    
    from wgeng.settings          import GEOSERVER_SET, DATABASES
    from weapi.models            import Countries, Scale
    from gasp3.sql.mng.tbl       import del_tables
    from gasp3.web.geosrv.stores import del_store
    
    # Get Group Instance in Database
    grp_inst = Countries.objects.get(fid=int(idgrp))
    
    # Delete Store in Geoserver
    del_store(GEOSERVER_SET["WORKSPACE"], grp_inst.slug, conf=GEOSERVER_SET)
    
    # Delete Views in Database
    scales = Scale.objects.filter(id_grp=int(idgrp))
    del_tables(
        DATABASES['default'],
        ["{}_{}".format(grp_inst.slug, s.desig) for s in scales],
        isViews=True)
    
    # Delete
    grp_inst.delete()
    
    return HttpResponseRedirect('/gui/backoffice/pt/su/manage/?status=103')
