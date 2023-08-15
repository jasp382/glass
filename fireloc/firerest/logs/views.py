import datetime as dt
# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc

from logs.models import LogsToken, LogsAuth, LogsGeoRef, LogsGeoRst
from logs.models import LogsContrib, LogsEvents, LogsSdi, LogsGeovis
from logs.models import LogsFiredetect, LogsGeosat, LogsMeteo, LogsGeoVec

from logs.srl import LogsTokenSrl, LogsAuthSrl, LogsContribSrl
from logs.srl import LogsEventSrl, LogsSDISrl, LogsGeoRefSrl, LogsGeoRstSrl
from logs.srl import LogsGeovisSrl, LogsFiredetectSrl, LogsMeteoSrl, LogsGeosatSrl
from logs.srl import LogsVecSrl

# Create your views here.


class LogsList(APIView):
    """
    System Logs
    ---
    """

    parser_classes = [JSONParser]
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    def get(self, request, app, format=None):
        """
        Method GET - Retrieve a list with all existing Logs
        ---
        """

        if app == 'token':
            logMdl, logSrl = LogsToken, LogsTokenSrl
        
        elif app == 'auth':
            logMdl, logSrl = LogsAuth, LogsAuthSrl
        
        elif app == 'georef':
            logMdl, logSrl = LogsGeoRef, LogsGeoRefSrl
        
        elif app == 'georst':
            logMdl, logSrl = LogsGeoRst, LogsGeoRstSrl
        
        elif app == 'contrib':
            logMdl, logSrl = LogsContrib, LogsContribSrl

        elif app == 'events':
            logMdl, logSrl = LogsEvents, LogsEventSrl
        
        elif app == 'geosrv':
            logMdl, logSrl = LogsSdi, LogsSDISrl
        
        elif app == 'geovis':
            logMdl, logSrl = LogsGeovis, LogsGeovisSrl
        
        elif app == 'geovec':
            logMdl, logSrl = LogsGeoVec, LogsVecSrl
        
        elif app == 'firedetect':
            logMdl, logSrl = LogsFiredetect, LogsFiredetectSrl
        
        elif app == 'geosat':
            logMdl, logSrl = LogsGeosat, LogsGeosatSrl
        
        elif app == 'meteo':
            logMdl, logSrl = LogsMeteo, LogsMeteoSrl
        
        logdata = logMdl.objects.all().order_by('-datehour')[:100]
        srl = logSrl(logdata, many=True)

        code, msg = "S20", "Data successfully returned"

        return Response({
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, app, format=None):
        """
        Delete all existing logs for one application
        """

        if app == 'token':
            logMdl = LogsToken
        
        elif app == 'auth':
            logMdl = LogsAuth
        
        elif app == 'georef':
            logMdl = LogsGeoRef
        
        elif app == 'georst':
            logMdl = LogsGeoRst
        
        elif app == 'contrib':
            logMdl = LogsContrib

        elif app == 'events':
            logMdl = LogsEvents
        
        elif app == 'geosrv':
            logMdl = LogsSdi
        
        elif app == 'geovis':
            logMdl = LogsGeovis
        
        elif app == 'geovec':
            logMdl = LogsGeoVec
        
        elif app == 'firedetect':
            logMdl = LogsFiredetect
        
        elif app == 'geosat':
            logMdl = LogsGeosat
        
        elif app == 'meteo':
            logMdl = LogsMeteo
        
        logMdl.objects.all().delete()

        code, msg = "S20", "Data was deleted"

        return Response({
            "status" : {"code" : code, "message" : msg}
        }, status=status.HTTP_200_OK)

