"""
Graphical User Interface
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect

def red_cases(request):
    """
    Redirect
    """
    
    return HttpResponseRedirect('/gui/backoffice/pt/cases/manage/')


def mng_cases(request):
    """
    Manage Study Cases
    
    Options:
    list - list available study cases
    add  - add a new study case
    """
    
    SERVICE_META = {
        'name' : 'manage-study-cases',
        'app'  : 'atlas',
        'about': 'manage-service',
        'url'  : '/gui/backoffice/pt/cases/manage/'
    }
    
    if 'status' in request.GET and 'rqst' in request.GET:
        todo = int(request.GET['status'])
        rqst = request.GET['rqst'] 
    else:
        todo = 300
        rqst = 0
    
    return render(
        request, 'app/manage-cases.html', {
            'atlas_lang' : 'pt',
            'service'    : SERVICE_META,
            'todo'       : todo,
            'rqst'       : rqst
        }
    )

