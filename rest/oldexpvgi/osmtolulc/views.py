from django.http import HttpResponseRedirect

# Create your views here.
def down_osm_file(request):
    """
    Download OSM File
    """
    
    from api.settings import INTERFACE_DOMAIN, DEBUG
    from cpu          import SERVICES, URLS
    
    SERVNAME = SERVICES[1]
    URL      = URLS[SERVNAME]
    
    if request.method == 'GET':
        """
        Process data inserted in the forms
        
        Get Bounding Box and download OSM Data
        """
        
        RQST_ID  = request.GET['rqst_id']
        GEOM_STR = request.GET['geom']
        USER_ID  = request.GET['uid']
        
        if DEBUG:
            from osmtolulc.meth import down_osm_by_geom as down_by_geom
        else:
            from osmtolulc.meth import prod_down_osm_by_geom as down_by_geom
        
        status, rqst_fid = down_by_geom(RQST_ID, USER_ID, GEOM_STR)
        
        # Status 104 = Unknow Error
        if status != 104:
            return HttpResponseRedirect((
                '{}{}/?status={}&rqst={}&bb={}'
            ).format(
                INTERFACE_DOMAIN, URL, str(status), rqst_fid, str(status)
            ))
        
        else:
            return HttpResponseRedirect('{}/expvgi/error/{}/{}/'.format(
                INTERFACE_DOMAIN, SERVNAME, rqst_fid
            ))
    
    else:
        """
        Nothing to do, return to osm2lulc main page
        """
        
        return HttpResponseRedirect(
            '{}{}/'.format(INTERFACE_DOMAIN, URL)
        )


def run_osm2lulc(request):
    """
    Run OSM2LULC Procedure
    """
    
    from api.settings import INTERFACE_DOMAIN, DEBUG
    from cpu          import SERVICES, URLS
    
    SERVNAME = SERVICES[1]
    URL      = URLS[SERVNAME]
    
    if request.method == 'GET' and 'rqst_id' in request.GET:
        RQST_ID   = request.GET['rqst_id']
        NOMENCLAT = request.GET['nomenclature']
        
        if DEBUG:
            from osmtolulc.meth import go_osm2lulc as go_osm2lulc
        
        else:
            from osmtolulc.meth import prod_go_osm2lulc as go_osm2lulc
        
        status, rqst_fid = go_osm2lulc(RQST_ID, NOMENCLAT)
        
        if status != 106:
            return HttpResponseRedirect((
                '{}{}/?rqst={}&nomenclature={}&status=105'
            ).format(INTERFACE_DOMAIN, URL, rqst_fid, NOMENCLAT))
        else:
            return HttpResponseRedirect('{}/expvgi/error/osmtolulc/{}/'.format(
                INTERFACE_DOMAIN, rqst_fid
            ))
    
    else:
        """
        Nothing to do, return to osm2lulc main page
        """
        
        return HttpResponseRedirect(
            '{}{}/'.format(INTERFACE_DOMAIN, URL)
        )

