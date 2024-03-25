# REST Framework Dependencies

import os
import requests as rq
import xmltodict

from rest_framework.response import Response
from rest_framework          import status
from rest_framework.parsers  import JSONParser
from rest_framework          import generics

from django.http import HttpResponse, JsonResponse

from api.settings import DATABASES, GEOSERVER_CON
from gserver.tools import lst_views, q_to_ntbl
from pwtools.gsrv.lyrs import add_pglyr

from layers.models import Layers
from layers.srl import LayersSrl


class GeoServerLayers(generics.GenericAPIView):
    """
    """

    parser_classes = [JSONParser]

    def post(self, request, lid):
        db = DATABASES["default"]["NAME"]

        ws, store = GEOSERVER_CON['WORKSPACE'], GEOSERVER_CON["STORE"]

        # View name
        nview = f"layer_{str(lid)}"

        # List views
        eviews = lst_views(db)

        # See if view exists
        # Create view if not exists
        if nview not in eviews:
            q_to_ntbl(db, nview, (
                "SELECT * "
                "FROM geoms_geodata "
                f"WHERE layerid = {str(lid)}"
            ), ntblIsView=True)

        # Create Layer
        response = add_pglyr(nview, ws, store, 3763)

        rr = Response(response, status=status.HTTP_201_CREATED)

        return rr


class GeoServerLayersStyle(generics.GenericAPIView):
    """
    """

    parser_classes = [JSONParser]

    def post(self, request, lid):
        from pwtools.gsrv.sld import write_sld
        from pwtools.gsrv.sty import lst_styles, create_style
        from pwtools.gsrv.sty import assign_style_to_layer

        _status, http = None, None

        d = request.data

        mapattrkeys = {
            'r' : 'red', 'g' : 'green', 'b' : 'blue',
            'category' : 'cat', 'opacity' : 'opacity'
        }

        try:
            lyr = Layers.objects.get(pk=int(lid))
            slyr = LayersSrl(lyr)
            lyrd = slyr.data
        
        except Layers.DoesNotExist:
            _status, http = {
                "message" : "Layer doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            # Get symbology rules
            symb = []
            for i in range(len(d["classes"])):
                symb.append({
                    'cat'     : str(d["classes"][i]),
                    'red'     : d["red"][i],
                    'blue'    : d["blue"][i],
                    'green'   : d["green"][i],
                    'opacity' : 1
                })
        
            # Write SLD
            sld = write_sld(
                'code', symb, mapattrkeys,
                os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    'data', f'sld_lyr_{str(lid)}.sld'
                ), geometry='Polygon', DATA='CATEGORICAL'
            )

            # Create style
            sn = 0
            if not lyrd["style"]:
                nstyle = f'lyr_{str(lid)}_style_0'
            
            else:
                sn = int(lyrd["style"].split('_')[-1])
                nstyle = f'lyr_{str(lid)}_style_{str(sn + 1)}'
                
            create_style(nstyle, sld)

            # Relate style with layer
            assign_style_to_layer(nstyle, f"layer_{str(lid)}")

            # Update layer
            lyrd["style"] = nstyle

            srl = LayersSrl(lyr, data=lyrd)

            if srl.is_valid():
                srl.save()

                response = {'message' : 'everything as expected'}
                http = status.HTTP_201_CREATED
            
            else:
                response = str(srl.errors)
                http = status.HTTP_400_BAD_REQUEST
        
        else:
            response = _status
        
        rr = Response(response, status=http)

        return rr


def get_wms(request, work):
    """
    Get WMS
    """

    h, p = GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT']

    url = f'http://{h}:{p}/geoserver/{work}/wms?'

    r = rq.get(url, params={
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

    h, p = GEOSERVER_CON['HOST'], GEOSERVER_CON['PORT']

    # Get XML Data
    xml_data = rq.get((
        f'http://{h}:{p}/geoserver/wms?request=GetCapabilities&'
        'service=WMS&version=1.1.1'
    ), allow_redirects=True)

    # XML to Dict
    dict_data = xmltodict.parse(xml_data.content)

    # Get Layer Information
    LYR_NAME = f'{work}:{lyr}'
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

    r = rq.get(url, headers={'Accept' : 'application/json'})
    wfs = r.json()

    return JsonResponse(wfs, content_type='json')


def get_featinfo(request, work, lyr):
    """
    Geoserver getFeatureInfo data to a Json Response
    """

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

    r = rq.get(url, headers={'Accept': 'application/json'})

    return JsonResponse(r.json())


def get_legend_ml(request, work):
    """
    Get Layer Legend for many layers
    """

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

        r = rq.get(url, headers={'Accept' : 'application/json'})

        legdata.append(r.json())

    return JsonResponse(legdata, safe=False)

