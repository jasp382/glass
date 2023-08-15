"""
Parse Web Map Service to the Client
"""

import requests as rqst
import datetime as dt
import pytz

from osgeo import ogr

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from logs.srl import LogsSDISrl

from glass.firecons.gsrv import con_gsrv


class GetWFS(APIView):
    """
    Return WFS in JSON
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, work, lyr):
        """
        Method GET - GeoServer -> Pass Web Feature Service using Django
        ---
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        qp = request.query_params

        operators = { 
            'e' : '=', 'l' : '<',
            'loe' : '<=', 'g' : '>',
            'goe' : '>=', 'd' : "!="
        }

        if 'filter' in qp:
            flt = qp['filter'].split(';')

            if 'opt' in qp:
                opts = qp['opt'].split(';')

                _signals = [operators.get(opt, '=')  for opt in opts]
            
            else:
                _signals = ['='] * len(flt)
            
            _params = []
            for idx, p in enumerate(flt, start=0):
                attr, val = p.split(':')

                try:
                    _val = int(val)

                    _params.append(f"{attr}{_signals[idx]}{val}")
                
                except:
                    _params.append(f"{attr}{_signals[idx]}'{val}'")
            
            filters = " AND ".join(_params)
        
        else:
            filters = ''
        
        epsg = "4326" if "epsg" not in qp else str(qp["epsg"])

        if "bbox" not in qp:
            bbox = ""
        else:
            bbox_epsg = qp.get("bboxsrs", None)

            if not filters:
                geom = ogr.CreateGeometryFromWkt(qp['bbox'])

                _bbox = geom.GetEnvelope()

                bbox_ = [_bbox[0], _bbox[2], _bbox[1], _bbox[3]]

                epsgstr = '' if not bbox_epsg else f",EPSG:{str(bbox_epsg)}"

                bboxstr = ",".join([str(c) for c in bbox_]) + epsgstr

                bbox = f"bbox={bboxstr}&"
            
            else:
                bbox=""
                filters = f"{filters} AND intersects(geom,{qp['bbox']})"

        if "datehour" in qp:
            timecheck = 1
            dtime = {}

            for st in ["startime", "endtime"]:
                if st not in qp: continue

                try:
                    tt = dt.datetime.strptime(qp[st], '%Y-%m-%d-%H-%M-%S')

                    dtime[st] = tt.strftime('%Y-%m-%d %H:%M:%S')
                
                except:
                    timecheck = 0
                
            if timecheck:
                filters = f"{filters} AND " if filters else ""

                if "startime" in qp and "endtime" in qp:
                    filters = (
                        f'{filters}{qp["datehour"]} '
                        f'BETWEEN \'{dtime["startime"]}\' AND \'{dtime["endtime"]}\''
                    )
        
                elif "startime" in qp and "endtime" not in qp:
                    filters = f'{filters}{qp["datehour"]} > \'{dtime["startime"]}\''
        
                elif "startime" not in qp and "endtime" in qp:
                    filters = f'{filters}{qp["datehour"]} < \'{dtime["endtime"]}\''

        q_ = '' if not filters else f'cql_filter={filters}'
        
        _c = '' if 'count' not in qp else f'&count={str(qp["count"])}'

        url = (
            f'{G["PROTOCOL"]}://{G["HOST"]}:'
            f'{G["PORT"]}/geoserver/wfs?'
            'service=wfs&version=2.0.0&request=GetFeature&'
            f'typeNames={work}:{lyr}&'
            f'srsName=EPSG:{epsg}{_c}&{q_}&{bbox}'
            'outputFormat=application/json'
        )

        try:
            r = rqst.get(url, headers={'Accept' : 'application/json'})
            
            if r.status_code == 200:
                msg = "Data successfully returned"

                response, http = {
                    "status" : {"code" : "S20", "message" : msg},
                    "layer"  : lyr,
                    "data"   : r.json()
                }, status.HTTP_200_OK
                
            elif r.status_code == 400:
                response, http = {"layer": lyr, "status" : {
                    "code"    : "GS2",
                    "message" : str(r.content)
                }}, status.HTTP_404_NOT_FOUND
            
            elif r.status_code == 404:
                response, http = {"layer": lyr, "status" : {
                    "code"    : "GS2",
                    "message" : "Workspace doesn't exist"
                }}, status.HTTP_404_NOT_FOUND
            
            else:
                response, http = {"layer": lyr, "status" : {
                    "code"    : "GS2",
                    "message" : str(r.content)
                }}, status.HTTP_404_NOT_FOUND
            
        except:
            response, http = {"layer": lyr, "status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST

        rr = Response(response, status=http)
        
        # Write Logs
        li = LogsSDISrl(data={
            'url'      : f'geosrv/wfs/{work}/{lyr}/',
            'service'  : 'geoserver-wfs',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None
        })

        if li.is_valid(): li.save()
        
        return rr


def get_wms(request, work):
    """
    Method GET - Get Web Map Service
    ---
    """

    from django.http import HttpResponse

    G = con_gsrv()

    r = rqst.get((
        f"{G['PROTOCOL']}://{G['HOST']}:"
        f"{G['PORT']}/geoserver/{work}/wms?"
    ), params={
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

