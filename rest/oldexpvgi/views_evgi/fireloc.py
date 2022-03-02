from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse


def fire_redirect(request):
    """
    Redirect
    """
    
    return HttpResponseRedirect('/expvgi/fire/report/')


def fire_report(request):
    """
    Report a fire occurence
    
    Mobile Version
    """
    
    from api.settings import MODULES_DOMAIN
    
    whatis = 'end' if 'status' in request.GET else 'start'
    
    return render(request, 'services/fireloc-report-mobile.html', {
        'whatis'           : whatis,
        'INTERFACE_DOMAIN' : MODULES_DOMAIN
    })

