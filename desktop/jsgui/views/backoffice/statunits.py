"""
Manage Geometries of Statistic Unities in Platform
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect


def red_su(request):
    """
    Redirect
    """
    
    return HttpResponseRedirect('/gui/backoffice/pt/su/manage/')


def mng_su(request):
    """
    Manage Countries and Statistic Units
    """
    
    SERVICE_META = {
        'name'  : 'manage-countries-stats',
        'app'   : 'atlas',
        'about' : 'manage-service',
        'url'   : 'pt/atlas/stat-units/manage/'
    }
    
    if 'status' in request.GET and 'rqst' in request.GET:
        todo = request.GET['status']
        rqst = request.GET['rqst']
    else:
        todo = 100
        rqst = 0
    
    return render(request, 'app/manage-stat-units.html', {
        'atlas_lang' : 'pt',
        'service' : SERVICE_META,
        'todo'    : todo,
        'rqst'    : rqst
    })