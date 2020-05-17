"""
GeotimeLine Views
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect

def gtml_redirect(request):
    """
    Redirect
    """
    
    return HttpResponseRedirect('/expvgi/gtl/geotimeline/')


def geotimeline(request):
    """
    GeoTimeLine Mechanism
    """
    
    from interface import SERVICES
    
    SERVICE_META = SERVICES[3]
    
    return render(request, 'services/geotimeline.html', {
        'service' : SERVICE_META
    })

