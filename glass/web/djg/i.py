"""
Information about Django Project
"""

def list_djg_apps(path_to_django_proj):
    """
    List Django App's avaiable in a Django Project
    """
    
    import os
    from glass.pyt.oss import list_folders_subfiles
    
    # Get project name
    projectName = os.path.basename(path_to_django_proj)
    
    # List folders and files in the folders
    projFolders = list_folders_subfiles(
        path_to_django_proj, files_format='.py',
        only_filename=True
    )
    
    apps = []
    # Check if the folder is a app
    for folder in projFolders:
        if os.path.basename(folder) == projectName:
            continue
        
        if '__init__.py' in projFolders[folder] or \
           'apps.py' in projFolders[folder]:
            apps.append(os.path.basename(folder))
    
    return apps

