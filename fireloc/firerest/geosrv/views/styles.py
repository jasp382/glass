"""
Manage Syles
"""

import datetime as dt
import pytz
import requests as rqsts
import os

# REST Framework Dependencies
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework          import permissions
from rest_framework.parsers  import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc
from firerest.utils    import check_rqst_param

from logs.srl import LogsSDISrl

from glass.firecons.gsrv import con_gsrv


class GeoServerStyles(APIView):
    """
    List/Create/Delete Styles in GeoServer
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        GET - List Styles
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        msg = "Data successfully returned"

        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:"
            f"{G['PORT']}/geoserver/rest/styles"
        )

        try:
            r = rqsts.get(
                url, headers={'Accept': 'application/json'},
                auth=(G["USER"], G["PASSWORD"])
            )

            if r.status_code == 200:
                rsp = [] if r.json()["styles"] == '' else \
                    r.json()['styles']["style"]
                
                response, sc = {
                    "status": {"code": "S20", "message": msg},
                    "data"    : rsp
                }, status.HTTP_200_OK
            
            else:
                response, sc = {"status" : {
                    "code"    : "GS2",
                    "message" : r.content
                }}, status.HTTP_404_NOT_FOUND
        
        except:
            response, sc = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        fresp = Response(response, status=sc)

        li = LogsSDISrl(data={
            'url'      : 'geosrv/styles/',
            'service'  : 'geoserver-styles',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    def post(self, request):
        """
        POST - Create new style
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, G = request.data, con_gsrv()

        # Check if parameters are valid
        p = ["name"]

        _status, http = check_rqst_param(p, d)

        # Add new style
        if not _status:
            url = (
                f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
                f"geoserver/rest/styles"
            )

            xml = (
                '<style>'
                    f'<name>{d["name"]}</name>'
                    f'<filename>sld_{d["name"]}.xml</filename>'
                '</style>'
            )

            try:
                r = rqsts.post(
                    url, data=xml, headers={'content-type': 'text/xml'},
                    auth=(G["USER"], G["PASSWORD"])
                )

                if r.status_code == 201:
                    response, http = {"status" : {
                        "code" : "G21",
                        "message" : "New GeoServer style was created"
                    }}, status.HTTP_201_CREATED
                
                else:
                    response, http = {"status" : {
                        "code"    : "GS2",
                        "message" : "Unknown error"
                    }}, status.HTTP_400_BAD_REQUEST
            
            except:
                response, http = {"status" : {
                    "code"    : "GS1",
                    "message" : "Can't connect to GeoServer"
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}

        fr = Response(response, status=http)

        li = LogsSDISrl(data={
            'url'      : 'geosrv/styles/',
            'service'  : 'geoserver-styles',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr


class GeoServerStyle(APIView):
    """
    Add SLD data to Style and delete a style
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def put(self, request, style):
        """
        Add SLD data to Style
        """

        from glass.wg.sld import write_sld, write_raster_sld

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, G = request.data, con_gsrv()

        # Check if parameters are valid
        fvalues = ["raster", "polygon", "linestring", "point"]

        p = ["symbology", "layertype", "datatype"]

        _status, http = check_rqst_param(p, list(d.keys()))

        if not _status and d['layertype'] != 'raster':
            p.append("attr")

            _status, http = check_rqst_param(p, list(d.keys()))

        # Create SLD file
        if not _status:
            sld_ = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'gsrvtmp', f"sld_{style}.xml"
            )

            if d['layertype'] == 'raster':
                sld = write_raster_sld(d["symbology"], sld_, dataType=d['datatype'])
            
            else:
                sld = write_sld(
                    p["attr"], d["symbology"], {k : k for k in d["symbology"]},
                    sld_, geometry=d["geomtype"], DATA=d["datatype"]
                )
        
            # Add SLD data to style
            url = (
                f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}"
                f"/geoserver/rest/styles/{style}"
            )

            with open(sld, 'rb') as f:
                try:
                    r = rqsts.put(
                        url, data=f,
                        headers={'content-type': 'application/vnd.ogc.sld+xml'},
                        auth=(G["USER"], G["PASSWORD"])
                    )

                    if r.status_code == 200:
                        response, http = {"status" : {
                            "code"    : "G22",
                            "message" : "SLD data was added to style"
                        }}, status.HTTP_201_CREATED
                
                    else:
                        response, http = {"status" : {
                            "code"    : "GS2",
                            "message" : "Unknown error"
                        }}, status.HTTP_400_BAD_REQUEST
            
                except:
                    response, http = {"status" : {
                        "code"    : "GS1",
                        "message" : "Can't connect to GeoServer"
                    }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        fr = Response(response, status=http)

        li = LogsSDISrl(data={
            'url'      : f'geosrv/style/{style}/',
            'service'  : 'geoserver-style',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr
    
    def delete(self, request, style):
        """
        Delete style
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        G = con_gsrv()

        url = (
            f"{G['PROTOCOL']}://{G['HOST']}:{G['PORT']}/"
            f"geoserver/rest/styles/{style}?recurse=true"
        )

        try:
            r = rqsts.delete(url, auth=(G["USER"], G["PASSWORD"]))

            if r.status_code == 200:
                response, http = {"status" : {
                    "code"    : "G23",
                    "message" : "Style was deleted"
                }}, status.HTTP_201_CREATED
                
            else:
                response, http = {"status" : {
                    "code"    : "GS2",
                    "message" : "Unknown error"
                }}, status.HTTP_400_BAD_REQUEST
        
        except:
            response, http = {"status" : {
                "code"    : "GS1",
                "message" : "Can't connect to GeoServer"
            }}, status.HTTP_400_BAD_REQUEST
        
        fr = Response(response, status=http)

        li = LogsSDISrl(data={
            'url'      : f'geosrv/style/{style}/',
            'service'  : 'geoserver-style',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr

