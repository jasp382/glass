"""
Pseudo Views for download
"""


def down_zip(zipf):
    """
    Prepare Download response for a zipped file
    """
    
    import os
    from django.http import HttpResponse
    
    with open(zipf, 'rb') as f:
        r = HttpResponse(f.read())
        
        r['content_type'] = 'application/zip'
        r['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(zipf)
        )
        
        return r


def down_xml(fileXml):
    """
    Prepare Download response for a xml file
    """
    
    import os
    from django.http import HttpResponse
    
    with open(fileXml, 'rb') as f:
        r = HttpResponse(f.read())
        
        r['content_type'] = 'text/xml'
        
        r['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(fileXml)
        )
        
        return r


def down_tiff(tifFile):
    """
    Download tif image
    """
    
    import os
    from django.http import HttpResponse
    
    with open(tifFile, mode='rb') as img:
        r = HttpResponse(img.read())
        
        r['content_type'] = 'image/tiff'
        r['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(tifFile)
        )
        return r

def down_bigzip(bigfile):
    """
    Download big file
    """

    import os
    from django.http import StreamingHttpResponse

    response = StreamingHttpResponse(open(bigfile, 'rb'))

    response['content-type'] = 'application/x-gzip'
    response['Content-Disposition'] = 'attachment;filename={}'.format(
        os.path.basename(bigfile)
    )

    return response


def mdl_to_kml(mdl, outKml, filter=None):
    """
    Query a database table and convert it to a KML File
    """
    
    import os
    from django.http               import HttpResponse
    from glass.pys.oss             import fprop
    from glass.webg.djg.mdl.serial import mdl_serialize_to_json
    from glass.it.shp            import shp_to_shp
    
    # Write data in JSON
    JSON_FILE = os.path.join(
        os.path.dirname(outKml), fprop(outKml, 'fn') + '.json'
    )
    
    mdl_serialize_to_json(mdl, 'geojson', JSON_FILE, filterQ=filter)
    
    # Convert JSON into KML
    shp_to_shp(JSON_FILE, outKml, gapi='ogr')
    
    # Create a valid DOWNLOAD RESPONSE
    with open(outKml, 'rb') as f:
        response = HttpResponse(f.read())
        
        response['content_type'] = 'text/xml'
        response['Content-Disposition'] = 'attachment;filename={}'.format(
            os.path.basename(outKml)
        )
        
        return response
