"""
Relate some geographic entities with the nearest place
"""

import datetime as dt
import pytz

# Rest Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc
from firerest.settings import DATABASES


class RelRealFirePlaces(APIView):
    """
    Relate real fire events with one Place
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def put(self, request, format=None):
        """
        Update relationships
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        db = DATABASES["default"]["NAME"]

        # Get near places


        fresp = Response({}, status=status.HTTP_201_CREATED)

        return fresp

