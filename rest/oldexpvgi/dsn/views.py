from django.shortcuts import render
from django.http      import HttpResponseRedirect

# Create your views here.


def get_data_fm_dsn(request):
    """
    Query and extract data from Digital Social Network
    """
    
    from api.settings import INTERFACE_DOMAIN, DEBUG
    
    if request.method == 'GET':
        if 'rqst_id' in request.GET and 'circle' in request.GET and \
            'sources' in request.GET:
            """
            Process data inserted in the forms
            
            Extract DSN Data
            """
            
            RQST_ID  = request.GET['rqst_id']
            GEOM_STR = request.GET['circle']
            USER_ID  = request.GET['uid']
            SOURCES  = request.GET['sources']
            KEYWORD  = None if request.GET['kw'] == 'None' else request.GET['kw']
            
            if DEBUG:
                from dsn.meth import query_dsn
            else:
                from dsn.meth import p_query_dsn as query_dsn
            
            status, rqst_fid = query_dsn(
                RQST_ID, GEOM_STR, SOURCES, KEYWORD, USER_ID
            )
            
            if status:
                return HttpResponseRedirect((
                    '{}/expvgi/dsn/mapsearch/?status={}&rqst={}'
                ).format(
                    INTERFACE_DOMAIN, status, rqst_fid
                ))
                
            else:
                return HttpResponseRedirect('{}/expvgi/error/mapsearch/{}/'.format(
                    INTERFACE_DOMAIN, rqst_fid
                ))
        
        else:
            return HttpResponseRedirect(
                '{}/expvgi/dsn/mapsearch/'.format(INTERFACE_DOMAIN)
            )
    else:
        return HttpResponseRedirect(
            '{}/expvgi/dsn/mapsearch/'.format(INTERFACE_DOMAIN)
        )

