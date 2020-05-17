"""
Deal with files
"""


def save_file(save_fld, _file):
    """
    Store a uploaded file in a given folder
    """ 
    
    import os
    
    file_out = os.path.join(save_fld, _file.name)
    with open(file_out, 'wb+') as destination:
        for chunk in _file.chunks():
            destination.write(chunk)
    
    return file_out

