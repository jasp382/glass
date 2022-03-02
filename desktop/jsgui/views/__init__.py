"""
Frontend Views
"""

from django.shortcuts import render
from django.http      import HttpResponseRedirect


def redirect_home(request, lang):
    """
    Redirect to Home
    """
    
    return HttpResponseRedirect('gui/{}/home/'.format(lang))


def app_meta(request, lang, meta):
    """
    Return pages with Meta Information
    """
    
    if lang != 'pt' and lang != 'es':
        return HttpResponseRedirect('gui/pt/{}/'.format(meta))
    
    if meta == 'organigrama':
        SERVICE_META = {
            'name'  : 'meta-organiza',
            'app'   : 'atlas',
            'about' : 'mega-page',
            'url'   : 'organigrama/'
        }
    
    elif meta == 'links':
        SERVICE_META = {
            'name'  : 'meta-links',
            'app'   : 'atlas',
            'about' : 'meta-page',
            'url'   : 'links/'
        }
    
    elif meta == 'contacts':
        SERVICE_META = {
            'name'  : 'meta-contact',
            'app'   : 'atlas',
            'about' : 'meta-page',
            'url'   : 'contacts/'
        }
    
    elif meta == 'project':
        SERVICE_META = {
            'name'  : 'meta-project',
            'app'   : 'atlas',
            'about' : 'meta-page',
            'url'   : 'project/'
        }
    
    elif meta == 'home':
        SERVICE_META = {
            'name'  : 'meta-home',
            'app'   : 'atlas',
            'about' : 'meta-page',
            'url'   : 'home/'
        }
    
    else:
        return HttpResponseRedirect('gui/{}/home/'.format(lang))
    
    return render(request, 'meta/{}.html'.format(
        SERVICE_META['name']
    ), {
        'service'    : SERVICE_META,
        'atlas_lang' : lang if lang == 'es' else 'pt'
    })

