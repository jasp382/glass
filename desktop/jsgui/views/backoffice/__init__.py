from django.shortcuts import render

from django.http import HttpResponseRedirect

def red_backoffice1(request):
    return HttpResponseRedirect('/gui/backoffice/pt/general/')


def red_backoffice2(request, lang):
    return HttpResponseRedirect('/gui/backoffice/pt/general/')


def backoffice(request):
    """
    Backoffice page
    """
    
    SERVICE_META = {
        'name' : 'manage-general',
        'app'  : 'atlas',
        'about': 'manage-service' ,
        'url'  : 'pt/atlas/general/'
    }
    
    return render(request, 'app/manage-general.html', {
        'atlas_lang' : 'pt',
        'service'    : SERVICE_META
    })

