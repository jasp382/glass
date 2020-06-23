"""
GeoServer Views
"""

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser


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

    return HttpResponse(r.content, content_type="image/png")


class GetWfs(APIView):
    """
    Return WFS in JSON
    """

    parser_classes = [JSONParser]

    def get(self, request, work, lyr, format=None):
        """
        GeoServer - Pass Web Feature Service using Django
        """

        import requests
        from glass.cons.gsrv import con_gsrv

        consrv = con_gsrv()

        # Request data
        data = request.data

        if 'val' in data and 'attr' in data:
            _q = '&cql_filter={}=\'{}\''.format(
                data['attr'], data['val']
            )

        else:
            _q = ''
    
        if 'count' in data:
            _c = '&count={}'.format(str(data['count']))
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

        return Response(wfs, status=status.HTTP_200_OK)


class FeatureInfo(APIView):
    """
    Return GetFeatureInfo
    """
    def get(self, request, work, lyr, format=None):
        """
        Geoserver getFeatureInfo data to a Json Response
        """

        import requests
        from glass.cons.gsrv import con_gsrv

        consrv = con_gsrv()

        data = request.data

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
            work=work, lyr=lyr, width=data['WIDTH'], height=data['HEIGHT'],
            x=data['X'], y=data['Y'], bbox=data['BBOX']
        )

        r = requests.get(url, headers={'Accept': 'application/json'})

        return Response(r.json(), status=status.HTTP_200_OK)


class LayerExtent(APIView):
    def get(self, request, work, lyr, format=True):
        """
        Return layer extent AS JSON RESPONSE
        """

        from glass.web.geosrv.prop import lyrext

        # Get layer extent
        extent = lyrext(work, lyr)
    
        return Response(extent, status=status.HTTP_200_OK)

