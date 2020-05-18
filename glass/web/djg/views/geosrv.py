"""
GeoServer Views
"""

def get_wms(request, work):
    """
    Get Web Map Service
    """

    import requests
    from django.http    import HttpResponse
    from glass.cons.gsrv import con_gsrv

    srvcon = con_gsrv()

    r = requests.get('{}://{}:{}/geoserver/{}/wms?'.format(
        srvcon['PROTOCOL'], srvcon['HOST'], srvcon['PORT'], work
    ),params={
        'service'     : request.GET['service'],
        'version'     : request.GET['version'],
        'request'     : request.GET['request'],
        'layers'      : request.GET['layers'],
        'width'       : request.GET['width'],
        'height'      : request.GET['height'],
        'bbox'        : request.GET['bbox'],
        'format'      : request.GET['format'],
        'transparent' : request.GET['transparent'],
        'styles'      : request.GET['styles'],
        'srs'         : request.GET['srs']
    })

    return HttpResponse(r.content)


def get_wfs(request, work, lyr):
    """
    GeoServer - Pass Web Feature Service using Django
    """

    import requests
    from django.http    import JsonResponse
    from glass.cons.gsrv import con_gsrv

    consrv = con_gsrv()

    if 'val' in request.GET and 'attr' in request.GET:
        _q = '&cql_filter={}=\'{}\''.format(
            request.GET['attr'], request.GET['val']
        )

    else:
        _q = ''
    
    if 'count' in request.GET:
        _c = '&count={}'.format(str(request.GET['count']))
    else:
        _c = ''

    url = (
        '{pr}://{host}:{port}/geoserver/{work_}/ows?'
        'service=WFS&version=2.0.0&request=GetFeature&'
        'typeName={work_}:{lyrn}&outputFormat=application/json&'
        '{c}{q}'
    ).format(
        pr=consrv['PROTOCOL'], host=consrv['HOST'], port=consrv['PORT'],
        work_=work, lyrn=lyr, q=_q, c=_c
    )

    r = requests.get(url, headers={'Accept' : 'application/json'})
    wfs = r.json()

    return JsonResponse(wfs, content_type='json')


def get_featinfo(request, work, lyr):
    """
    Geoserver getFeatureInfo data to a Json Response
    """

    import requests
    from django.http    import JsonResponse
    from glass.cons.gsrv import con_gsrv

    consrv = con_gsrv()

    url = (
        '{pr}://{host}:{port}/geoserver/wfs?'
        'INFO_FORMAT=application/json&'
        'REQUEST=GetFeatureInfo&EXCEPTIONS=application/vnd.ogc.se_xml&'
        'SERVICE=WMS&VERSION=1.1.1&'
        'WIDTH={width}&HEIGHT={height}&'
        'X={x}&Y={y}&BBOX={bbox}&LAYERS={work}:{lyr}&'
        'QUERY_LAYERS={work}:{lyr}&TYPENAME={work}:{lyr}&'
        'CRS=EPSG:4326'
    ).format(
        pr=consrv['PROTOCOL'], host=consrv['HOST'], port=consrv['PORT'],
        work=work, lyr=lyr,
        width=request.GET['WIDTH'], height=request.GET['HEIGHT'],
        x=request.GET['X'], y=request.GET['Y'],
        bbox=request.GET['BBOX']
    )

    r = requests.get(url, headers={'Accept': 'application/json'})

    return JsonResponse(r.json())


def get_extent(request, work, lyr):
    """
    Return layer extent AS JSON RESPONSE
    """

    from django.http          import JsonResponse
    from glass.web.geosrv.prop import lyrext

    # Get layer extent
    extent = lyrext(work, lyr)
    
    return JsonResponse(extent, content_type='json')

