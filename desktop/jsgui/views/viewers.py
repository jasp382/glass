"""
Views for viewers of GeoInformation and Maps
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

#@login_required(login_url='/head/quarters/accounts/login/')
def map_viewer(request, case):
    """
    Visualize information for Any Study Case
    """
    
    from weapi.models import StudyCases
    
    SERVICE_META = {
        'name'  : 'atlas-viewer-{}'.format(case),
        'app'   : 'atlas',
        'about' : 'viewer-service',
        'url'   : 'gui/pt/mapping/{}/'.format(case)
    }
    
    case_i = StudyCases.objects.get(slug=case)
    
    return render(request, 'app/map-viewer.html', {
        'service' : SERVICE_META,
        'atlas_lang' : 'pt',
        'mapsett' : {
            'fid'      : case_i.fid,
            'top'      : case_i.top,
            'bottom'   : case_i.bottom,
            'left'     : case_i.left,
            'right'    : case_i.right,
            'top_ctx'  : case_i.top_ctx,
            'bot_ctx'  : case_i.bottom_ctx,
            'left_ctx' : case_i.left_ctx,
            'right_ctx': case_i.right_ctx
        }
    })


def map_compare(request, case):
    """
    Comparing Viewer
    """
    
    from weapi.models import StudyCases
    
    SERVICE_META = {
        'name'  : 'atlas-viewer-{}'.format(case),
        'app'   : 'atlas',
        'about' : 'viewer-service',
        'url'   : 'gui/pt/compare/{}/'.format(case)
    }
    
    case_i = StudyCases.objects.get(slug=case)
    
    return render(request, 'app/map-compare.html', {
        'service' : SERVICE_META, 'atlas_lang' : 'pt',
        'mapsett' : {
            'fid'      : case_i.fid,
            'top'      : case_i.top,
            'bottom'   : case_i.bottom,
            'left'     : case_i.left,
            'right'    : case_i.right,
        }
    })

