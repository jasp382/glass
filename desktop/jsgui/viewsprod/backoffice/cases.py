"""
Graphical User Interface
"""

from wegui.viewsprod import ERROR_URL
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/head/quarters/accounts/login/')
def mng_cases(request):
    try:
        from wegui.views.backoffice.cases import mng_cases as ov
        
        return ov(request)
    except:
        return HttpResponseRedirect(ERROR_URL)

