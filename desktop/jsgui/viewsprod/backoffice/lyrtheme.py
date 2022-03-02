"""
Manage Theme Layers in WebGIS Engine
"""

from wegui.viewsprod import ERROR_URL
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/head/quarters/accounts/login/')
def mng_themelyr(request):
    try:
        from wegui.views.backoffice.lyrtheme import mng_themelyr as ov
        
        return ov(request)
    
    except:
        return HttpResponseRedirect(ERROR_URL)

