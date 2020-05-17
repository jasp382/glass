"""
Manage Theme Layers in WebGIS Engine
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect


def red_themelyr(request):
    """
    Redirect to Theme Layer Management
    """
    
    return HttpResponseRedirect('/gui/backoffice/pt/theme-lyr/manage/')


def mng_themelyr(request):
    """
    Manage Indicators:
    """
    
    SERVICE_META = {
        'name'  : 'manage-themelyr',
        'app'   : 'atlas',
        'about' : 'manage-service',
        'url'   : 'pt/atlas/lyr-themes/manage/'
    }
    
    if 'status' in request.GET and 'rqst_id' in request.GET:
        todo = request.GET['status']
        rqst = request.GET['rqst_id']
    
    else:
        todo = 200
        rqst = 0
    
    return render(request, 'app/manage-themelyr.html' , {
        'atlas_lang' : 'pt',
        'service'    : SERVICE_META,
        'todo'       : todo,
        'rqst'       : rqst
    })

