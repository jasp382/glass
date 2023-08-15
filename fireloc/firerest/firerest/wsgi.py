"""
WSGI config for firerest project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from firerest.settings import CTX, DATABASES

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'firerest.settings')

application = get_wsgi_application()

import django.core.handlers.wsgi

_application = django.core.handlers.wsgi.WSGIHandler()

def application(environ, start_response):
    try:
        os.environ['HOME'] = environ['STHOME']
        os.environ['PGPASSWORD']       = environ['STPGPASSWORD']
        os.environ['LANG']             = environ['STLANG']
        os.environ['LANGUAGE']         = environ['STLANGUAGE']
        os.environ['PYTHON_EGG_CACHE'] = environ['STEGG']
        os.environ['GDAL_DATA']        = environ["STGDALDATA"]
        os.environ['PROJ_LIB']         = environ["STPROJLIB"]
        os.environ['LD_LIBRARY_PATH']  = environ["STLD_LIBRARY_PATH"]
    except:
        os.environ['HOME']             = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ['PGPASSWORD']       = DATABASES["default"]["PASSWORD"]
        os.environ['LANG']             = 'pt_PT'
        os.environ['LANGUAGE']         = 'pt'
        os.environ['PYTHON_EGG_CACHE'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ['GDAL_DATA']        = CTX["APACHE"]["GDAL_DATA"]
        os.environ['PROJ_LIB']         = CTX["APACHE"]["PROJ_LIB"]
        os.environ['LD_LIBRARY_PATH']  = CTX["APACHE"]["LIB_GDAL"]
    
    return _application(environ, start_response)