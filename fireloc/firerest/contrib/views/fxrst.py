"""
Deal with Contributions related files
"""


import datetime as dt
import pytz
import mimetypes
import os

# REST Framework Dependencies
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework          import status
from rest_framework          import permissions
from rest_framework.parsers  import JSONParser
from django.http.response import HttpResponse

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.settings import GEOMEDIA_FOLDERS

from contrib.models import VolunteersContributions

from logs.srl import LogsContribSrl


class DownFxFile(APIView):
    """
    Download Strip file
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, ctb):
        """
        Get file and return it
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        dfolder = GEOMEDIA_FOLDERS.get('CTB_RASTER', None)
        rst = os.path.join(dfolder, f"ctbfx_{str(ctb)}.tif")

        # Check if contribution exists
        try:
            ctb_ = VolunteersContributions.objects.get(fid=int(ctb))

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Check if file exists
        if not _status and not os.path.exists(rst):
            _status, http = {
                "code"    : "I05",
                "message" : "Photo does not exist"
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            with open(rst, mode="rb") as img:
                r = HttpResponse(img.read())

                mt, _ = mimetypes.guess_type(rst)

                r['content_type'] = mt
                r['Content-Disposition'] = (
                    f'attachment;filename={os.path.basename(rst)}'
                )

                return r
        else:
            response = {"status" : _status}

            return Response(response, status=http)


class FxFile(APIView):
    """
    Deal with Contributions strips files
    """

    permission_classes = [
        permissions.IsAdminUser,
        TokenHasReadWriteScope
    ]

    def post(self, request, ctb):
        """
        Receive strip raster file and store it
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        dfolder = GEOMEDIA_FOLDERS.get('CTB_RASTER', None)

        # Check if contribution exists
        try:
            ctb_ = VolunteersContributions.objects.get(fid=int(ctb))

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Receive file and store it
        if not _status:
            fdata = request.FILES.get('fxrst')

            rst = os.path.join(dfolder, f"ctbfx_{str(ctb)}.tif")

            with open(rst, 'wb+') as rf:
                for chunk in fdata.chunks():
                    rf.write(chunk)
            
            response, http = {"status" : {
                "code"    : "S22",
                "message" : "Contribution was edited",
            }}, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        li = LogsContribSrl(data={
            'url'      : f'/volu/ctb-fx/{str(ctb)}/',
            'service'  : 'contribution-raster',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user
        })

        if li.is_valid(): li.save()

        return r

