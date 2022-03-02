"""
OSM Tools Views
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect


def osm_redirect(request):
    """
    Redirect to OSM2LULC Service
    """
    
    return HttpResponseRedirect('/expvgi/osm/osm2lulc/')


def osm2lulc(request):
    """
    View for OSM TO LULC Procedure
    """
    
    import os; from gui.settings   import DEBUG
    from interface                 import SERVICES
    from django.contrib.auth.forms import AuthenticationForm
    
    SERVICE_META = SERVICES[1]
    
    if request.method == 'POST':
        """
        Check in which Phase the user is
        """
        
        from gui.settings import MODULES_APP
        
        phase = request.POST['phase']
        
        if phase == 'down-phase':
            """
            Download OSM Data
            """
            
            from interface.utils import get_rqst_id
            
            # Get Information send it by the user!
            RQST_FID, USER_FID = get_rqst_id(request)
            
            # Get Geometry
            if request.POST['form_type'] == 'draw_bb':
                """
                Polygon is String
                """
                
                geom = request.POST['draw_rectangle'].replace(
                    ';', 'pv').replace(',', 's').replace('.', 'd')
            
            # Ask for a response from API
            return HttpResponseRedirect((
                '{}/api/osm2lulc/download/?rqst_id={}&'
                'geom={}&uid={}'
            ).format(MODULES_APP, RQST_FID, geom, USER_FID))
        
        elif phase == 'lulc-phase':
            """
            Ask to the API for OSM2LULC execution
            """
            
            RQST_FID  = str(request.POST['rqst'])
            NOMENCLA  = str(request.POST['nomenclature'])
            
            # Ask for a response from API
            return HttpResponseRedirect((
                '{}/api/osm2lulc/go/?rqst_id={}&nomenclature={}'
            ).format(MODULES_APP, RQST_FID, NOMENCLA))
        
        else:
            """
            Nothing to do!
            """
        
            return HttpResponseRedirect(SERVICE_META['url'])
    
    else:
        if 'bb' in request.GET:
            """
            Second phase of input parameters
            """
            
            STATUS = int(request.GET['status'])
            
            if STATUS == 101:
                from interface.forms.osmforms import OsmtolulcRun
            
                form = OsmtolulcRun(initial={
                    'rqst' : request.GET['rqst']
                })
            
            else:
                from interface.forms.osmforms import OsmtolulcDraw
                
                form = OsmtolulcDraw()
            
            if DEBUG:
                from django.contrib.auth import authenticate, login
                
                user = authenticate(request, username='kurosaki',
                                    password='kurosaki++zangetsu')
                
                login(request, user)
            
            return render(request, 'services/osm-to-lulc.html', {
                'service'   : SERVICE_META,
                'form'      : form,
                'auth_form' : AuthenticationForm(),
                'whatToDo'  : 's-inputs' if STATUS == 101 else 'f-inputs',
                'rqst_id'   : request.GET['rqst']
            })
        
        else:
            """
            Load page for the first time or show result
            """
        
            from ..forms.osmforms import OsmtolulcDraw
            
            if DEBUG:
                from django.contrib.auth import authenticate, login
                
                user = authenticate(request, username='kurosaki',
                                    password='kurosaki++zangetsu')
                
                login(request, user)
        
            drawForm = OsmtolulcDraw()
            
            r = request.GET['rqst'] if 'rqst' in request.GET else 'null'
        
            return render(request, 'services/osm-to-lulc.html', {
                'service'   : SERVICE_META,
                'form'      : drawForm,
                'auth_form' : AuthenticationForm(),
                'whatToDo'  : 'f-inputs',
                'rqst_id'   : r
            })

