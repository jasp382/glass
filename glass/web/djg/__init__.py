"""
Tools for Django
"""

def open_Django_Proj(path_to_proj):
    """
    To run methods related with django objects, we
    need to make our python recognize the Django Project
    """
    
    import os, sys
    
    # This is so Django knows where to find stuff.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "{}.settings".format(os.path.basename(path_to_proj))
    )
    
    sys.path.append(path_to_proj)
    
    # This is so my local_settings.py gets loaded.
    os.chdir(path_to_proj)
    
    # This is so models get loaded.
    from django.core.wsgi import get_wsgi_application
    
    return get_wsgi_application()

