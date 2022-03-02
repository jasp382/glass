"""
DSN Tools Views
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect


def dsn_redirect(request):
    """
    Redirect to DSN data Collection Service
    """
    
    return HttpResponseRedirect('/expvgi/dsn/mapdsn/')


def query_dsn(request):
    """
    Query data from Digital Social Networks as:
    - Facebook
    - Flickr
    - Twitter
    """
    
    from gui.settings              import DEBUG
    from django.contrib.auth.forms import AuthenticationForm
    
    # Service metadict
    SERVICE_META = {
        'name'   :  'mapsearch',
        'header' :  'Mapping Social Network Data',
        'app'    :  'expvgi',
        'url'    :  '/expvgi/dsn/mapsearch/',
        'about'  :  'service'
    }
    
    if request.method == 'POST':
        """
        Get DSN data from API
        """
        
        from gui.settings    import MODULES_APP
        from interface.utils import get_rqst_id
        
        # Create REQUEST ID
        RQST_FID, USER_FID = get_rqst_id(request)
        
        """
        Receive objects from the form
        - keyword
        - strings needed to create a buffer
        - data sources
        """
        
        keyword = 'None' if not request.POST['keyword'] else \
            request.POST['keyword']
        
        circle  = request.POST['draw_circle'].replace(';', 'pv').replace(
            ',', 's').replace('.', 'd')
        
        sources = request.POST['data_sources'].replace(';', 'pv')
        
        # Ask for a response from API
        return HttpResponseRedirect((
            '{}/api/dsn/mapsearch/?rqst_id={}&circle={}&uid={}&'
            'sources={}&kw={}'
        ).format(MODULES_APP, RQST_FID, circle, USER_FID, sources, keyword))
    
    else:
        """
        Load the page for the first time... or show results
        """
        
        from interface.forms.dsnsearch import SearchForPosts
        
        if DEBUG:
            from django.contrib.auth       import authenticate, login
            
            user = authenticate(
                request, username='kurosaki', password='kurosaki++zangetsu')
            
            login(request, user)
        
        r = request.GET['rqst'] if 'rqst' in request.GET else 'null'
        
        return render(request, 'services/dsn-map-search.html', {
            'form'      : SearchForPosts(),
            'service'   : SERVICE_META,
            'rqst_id'   : r,
            'auth_form' : AuthenticationForm()
        })

