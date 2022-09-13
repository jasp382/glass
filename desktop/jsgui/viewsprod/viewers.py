"""
Views for viewers of GeoInformation and Maps
"""

from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

ERROR_URL = '/pt/some/error/'

@login_required(login_url='/head/quarters/accounts/login/')
def map_viewer(request, case):
    try:
        from wegui.views.viewers import map_viewer as ov
        
        return ov(request, case)
    except:
        return HttpResponseRedirect(ERROR_URL)


@login_required(login_url='/head/quarters/accounts/login/')
def map_compare(request, case):
    try:
        from wegui.views.viewers import map_compare as ov
        
        return ov(request, case)
    except:
        return HttpResponseRedirect(ERROR_URL)

