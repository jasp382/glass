"""
Work with contributions photos
"""

import datetime as dt
import pytz
import mimetypes
import os


# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser
from django.http.response import HttpResponse

from glass.it.pht    import img_to_str

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.settings import GEOMEDIA_FOLDERS

from logs.srl import LogsContribSrl


class PhotoData(APIView):
    """
    Return photo_data
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, picname):
        """
        Get Photo data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        ppath = os.path.join(GEOMEDIA_FOLDERS["CTB_PHOTOS"], picname)

        if os.path.exists(ppath):
            photo_str = img_to_str(ppath)

            code, msg = "S20", "Data successfully returned"

            response, http = {
                "status" : {"code" : code, "message" : msg},
                "data"   : photo_str
            }, status.HTTP_200_OK

        else:
            response, http = {"status" : {
                "code"    : "I05",
                "message" : "Photo does not exist"
            }}, status.HTTP_400_BAD_REQUEST

        f_resp = Response(response, http)

        # Write Logs
        logs_i = LogsContribSrl(data={
            'url'      : f'volu/photo/{picname}/',
            'service'  : 'get-photo-data',
            'method'   : request.method,
            'http'     : f_resp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logs_i.is_valid(): logs_i.save()

        return f_resp


class DownloadPhoto(APIView):
    """
    Download Photo File
    """


    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, picname):
        """
        Return File response
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        ppath = os.path.join(GEOMEDIA_FOLDERS["CTB_PHOTOS"], picname)

        # Check if file exists
        if not _status and not os.path.exists(ppath):
            _status, http = {
                "code"    : "I05",
                "message" : "Photo does not exist"
            }, status.HTTP_400_BAD_REQUEST

        if not _status:
            with open(ppath, mode="rb") as img:
                r = HttpResponse(img.read())

                mt, _ = mimetypes.guess_type(ppath)

                r['content_type'] = mt
                r['Content-Disposition'] = (
                    f'attachment;filename={os.path.basename(ppath)}'
                )

                return r
        
        else:
            response = {"status" : _status}

            return Response(response, status=http)

