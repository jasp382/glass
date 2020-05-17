"""
Deal with GeoData inside Django App
"""


def save_geodata(request, field_tag, folder):
    """
    Receive a file with vectorial geometry from a form field:
    
    Store the file in the server
    
    IMPORTANT: this method will only work if the FORM that is receiving the 
    files allows multiple files
    """
    
    import os
    from glass.webg.djg.ff import save_file
    from glass.g.prop import vector_formats, raster_formats
    
    files = request.FILES.getlist(field_tag)
    
    # Save all files
    ff = []
    for f in files:
        save_file(folder, f)

        ffmt = os.path.splitext(f)[1]
        if ffmt in vector_formats or ffmt in raster_formats:
            ff.append(os.path.join(folder, f))
    
    return None if not len(ff) else ff[0] if len(ff) == 1 else ff

