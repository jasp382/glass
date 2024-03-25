from django.shortcuts import render

# Create your views here.

def map_view(request):
    return render(request, 'leaf/map.html')

def get_wms(request, work):
    """
    Get WMS
    """

    import requests
    from django.http import HttpResponse
    from leafdemo.settings import GEOSERVER_CON

    r = requests.get('http://{}:{}/geoserver/{}/wms?'.format(
        GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT'], work
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

    response = HttpResponse(r.content)
    response["content-type"] = 'image/png'
    return response


def get_extent(request, work, lyr):
    """
    Get Capabilities View
    """

    import requests
    import json
    import xmltodict
    from django.http import JsonResponse
    from leafdemo.settings import GEOSERVER_CON

    # Get XML Data
    xml_data = requests.get((
        'http://{}:{}/geoserver/wms?request=GetCapabilities&'
        'service=WMS&version=1.1.1'
    ).format(
        GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT']
    ), allow_redirects=True)

    # XML to Dict
    dict_data = xmltodict.parse(xml_data.content)

    # Get Layer Information
    LYR_NAME = '{}:{}'.format(work, lyr)
    lyrs_data = dict_data['WMT_MS_Capabilities']['Capability']['Layer']['Layer']

    # Get Response data
    resp = {}
    for k in lyrs_data:
        if k['Name'] == LYR_NAME:
            resp['min_x'] = k['LatLonBoundingBox']['@minx']
            resp['max_x'] = k['LatLonBoundingBox']['@maxx']
            resp['min_y'] = k['LatLonBoundingBox']['@miny']
            resp['max_y'] = k['LatLonBoundingBox']['@maxy']
    
    return JsonResponse(resp, content_type='json')

def get_wfs(request, work, lyr):
    """
    GeoServer - Pass WFS using Django
    """

    import requests
    from django.http         import JsonResponse
    from leafdemo.settings import GEOSERVER_CON

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
        'http://{host}:{port}/geoserver/{work_}/ows?'
        'service=WFS&version=2.0.0&request=GetFeature&'
        'typeName={work_}:{lyrn}&outputFormat=application/json'
        '{c}{q}'
    ).format(
        host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
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
    from django.http import JsonResponse
    from leafdemo.settings import GEOSERVER_CON

    url = (
        'http://{host}:{port}/geoserver/wfs?'
        'INFO_FORMAT=application/json&'
        'REQUEST=GetFeatureInfo&EXCEPTIONS=application/vnd.ogc.se_xml&'
        'SERVICE=WMS&VERSION=1.1.1&'
        'WIDTH={width}&HEIGHT={height}&'
        'X={x}&Y={y}&BBOX={bbox}&LAYERS={work}:{lyr}&'
        'QUERY_LAYERS={work}:{lyr}&TYPENAME={work}:{lyr}&'
        'CRS=EPSG:4326'
    ).format(
        host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
        work=work, lyr=lyr,
        width=request.GET['WIDTH'], height=request.GET['HEIGHT'],
        x=request.GET['X'], y=request.GET['Y'],
        bbox=request.GET['BBOX']
    )

    r = requests.get(url, headers={'Accept': 'application/json'})

    return JsonResponse(r.json())


def get_legend_ml(request, work):
    """
    Get Layer Legend for many layers
    """
    import requests
    from django.http import JsonResponse
    from leafdemo.settings import GEOSERVER_CON

    layers = request.GET['layers'].split(',')
    styles = request.GET['styles'].split(',')

    legdata = []

    for l in range(len(layers)):
        url = (
            'http://{host}:{port}/geoserver/wms?REQUEST=GetLegendGraphic&'
            'VERSION=1.0.0&FORMAT=application/json'
            '&LAYER={w}:{l}&style={s}'
        ).format(
            host=GEOSERVER_CON['HOST'], port=GEOSERVER_CON['PORT'],
            w=work, l=layers[l], s=styles[l]
        )

        r = requests.get(url, headers={'Accept' : 'application/json'})

        print(url)
        legdata.append(r.json())

    return JsonResponse(legdata, safe=False)

