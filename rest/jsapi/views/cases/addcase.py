"""
EndPoints to Add/Edit/Delete StudyCases
"""

from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add_case(request):
    """
    Add new study case
    """
    
    if request.method == 'POST':
        """
        Receive parameters from Form
        """
        
        from django.contrib.gis.geos import GEOSGeometry
        from wgeng.settings          import DATABASES, GEOSERVER_SET
        from weapi.models            import StudyCases, Countries
        from weapi.utils             import get_rqst_id
        from weapi.views.cases.tools import get_casegeom
        from gasp3.web.geosrv.stores import create_pgstore
        from gasp3.sql.fm            import Q_to_df
        from gasp3.sql.prop             import check_last_id
        from gasp3.sql.to            import df_to_db
        
        caseFID = get_rqst_id(request)
        
        a_data_type = request.POST['list-def-ext']
        case_name   = request.POST['case-name']
        case_desc   = request.POST['case-description']
        b_data_type = request.POST['list-def-ext-b']
        stats_grp   = int(request.POST['list-stats'])
        
        """
        Get Geometry for Study Area
        """
        geom, left, right, bottom, top = get_casegeom(request, caseFID, a_data_type)
        
        """
        Get Geometry for Context Area
        """
        geom_b, left_b, right_b, bottom_b, top_b = get_casegeom(
            request, caseFID, b_data_type, ctx=True)
        
        """
        Send Data to Database
        """
        case_i = StudyCases.objects.create(
            fid=caseFID,
            slug=case_name, descricao=case_desc,
            geom=GEOSGeometry(geom.ExportToWkt(), srid=4326),
            top=round(top, 12), bottom=round(bottom, 12),
            left=round(left, 12), right=round(right, 12),
            geom_ctx=GEOSGeometry(geom_b.ExportToWkt(), srid=4326),
            top_ctx=top_b, bottom_ctx=bottom_b,
            left_ctx=left_b, right_ctx=right_b,
            country=Countries.objects.get(fid=stats_grp),
            gstore=case_name
        )
        
        """
        Get Statistic Units inside study area
        """
        stat_specific = Q_to_df(DATABASES['default'], (
            "SELECT fid AS fidunit FROM ("
                "SELECT fid, ST_Area(ST_Intersection(su_geom, ca_geom)) AS area_m, "
                "ST_Area(su_geom) AS area_o FROM ("
                    "SELECT su.fid AS fid, ST_Transform(su.geom, 3857) AS su_geom, "
                    "ST_Transform(aca.geom, 3857) AS ca_geom "
                    "FROM weapi_statunit AS su, "
                    "weapi_studycases AS aca "
                    "WHERE su.country = {} AND ST_Intersects("
                        "ST_Transform(su.geom, 3857), ST_Transform(aca.geom, 3857)"
                    ") IS True"
                ") AS foo"
            ") AS tst WHERE ((area_m * 100) / area_o >= 99)"
        ).format(str(stats_grp)))
        
        lastId = check_last_id(DATABASES['default'], 'fid', 'weapi_statcase')
        stat_specific['fid']     = stat_specific.index + lastId + 1
        stat_specific['fidcase'] = caseFID
        
        df_to_db(DATABASES['default'], stat_specific, 'weapi_statcase', append=True)
        
        # Create DataStore in GeoServer
        create_pgstore(
            case_name, GEOSERVER_SET["WORKSPACE"],
            DATABASES['default'], GEOSERVER_SET
        )
    
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/?status=301')
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


@csrf_exempt
def del_case(request, case_id):
    """
    Delete Study Case
    """
    
    from gasp3.sql.mng.tbl       import del_tables
    from gasp3.web.geosrv.stores import del_store
    
    # Get Stuty cases model
    from wgeng.settings import GEOSERVER_SET, DATABASES
    from weapi.models   import StudyCases, LyrIndicators
    
    # Get Specific study case
    case_inst = StudyCases.objects.get(fid=int(case_id))
    
    # Get Layers in Case
    lyrs = LyrIndicators.objects.filter(id_case=int(case_id))
    
    # If Layer, delete Views in database
    tbls = [
        "lyr_{}".format(str(li.fid)) for li in lyrs
    ] + ["detr_{}".format(str(li.fid)) for li in lyrs]
    if len(tbls):
        del_tables(DATABASES['default'], tbls, isViews=True)
    
    # TODO: Delete styles in Geoserver
    
    # Delete Store in GeoServer
    del_store(
        GEOSERVER_SET["WORKSPACE"], case_inst.slug, conf=GEOSERVER_SET
    )
    
    # Delete that specific case
    case_inst.delete()
        
    return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/?status=302')


@csrf_exempt
def edit_case(request):
    """
    Edit an existing Study Case
    """
    
    if request.method == 'POST':
        """
        Receive data from FORM
        """
        
        from django.contrib.gis.geos import GEOSGeometry
        from weapi.models import StudyCases, Countries
        from weapi.views.cases.tools import get_casegeom
        
        case_fid = int(request.POST['fid-case'])
        
        # Check if there is changes
        case_slug = request.POST['case-name']
        case_desc = request.POST['case-description']
        
        if 'list-def-ext' in request.POST:
            # We have new Geographic Data
            a_data_type = request.POST['list-def-ext']
            
            g, l, r, b, t = get_casegeom(request, a_data_type)
            
            isGeomA = True
        else:
            isGeomA = None
        
        if 'list-def-ext-b' in request.POST:
            # We have new Geographic Data for Context Area
            b_data_type = request.POST['list-def-ext-b']
            
            gb, lb, rb, bb, tb = get_casegeom(request, b_data_type, ctx=True)
            
            isGeomB = True
        
        else:
            isGeomB = None
        
        if 'list-stats' in request.POST:
            lstStats = int(request.POST['list-stats'])
        else:
            lstStats = None
        
        
        """
        Update Case instance
        """
        
        case_i = StudyCases.objects.get(fid=case_fid)
        case_i.slug = case_slug; case_i.descricao = case_desc
        
        if isGeomA:
            case_i.geom=GEOSGeometry(g.ExportToWkt(), srid=4326)
            case_i.top=round(t, 12); case_i.bottom=round(b, 12)
            case_i.left=round(l, 12); case_i.right=round(r, 12)
            
        if isGeomB:
            case_i.geom_ctx=GEOSGeometry(gb.ExportToWkt(), srid=4326)
            case_i.top_ctx=round(tb, 12); case_i.bottom_ctx=round(bb, 12)
            case_i.left_ctx = round(lb, 12); case_i.right_ctx=round(rb, 12)
        
        if lstStats:
            case_i.country = countries.objects.get(fid=lstStats)
        
        case_i.save()
        
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/?status=3')
    
    else:
        return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')

