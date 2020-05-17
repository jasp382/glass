"""
Manage Geometries of Statistic Unities in Platform
"""

from wegui.viewsprod import ERROR_URL
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/head/quarters/accounts/login/')
def mng_su(request):
    try:
        from wegui.views.backoffice.statunits import mng_su as ov
        
        return ov(request)
    
    except:
        return HttpResponseRedirect(ERROR_URL)

