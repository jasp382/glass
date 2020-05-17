from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from wegui.viewsprod import ERROR_URL

@login_required(login_url='/head/quarters/accounts/login/')
def backoffice(request):
    try:
        from wegui.views.backoffice import backoffice as ov
        
        return ov(request)
    except:
        return HttpResponseRedirect(ERROR_URL)

