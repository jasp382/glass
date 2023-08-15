"""
Views to deal with the contributions positions azimutes
"""


import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope


from contrib.models import VolunteersContributions, VolunteersPositions
from contrib.models import VolunteersPositionsBackFront
from contrib.srl import ContribPositionsSrl, ContribPosistionsBackFrontSrl

from firerest.permcls import IsFireloc

from logs.srl import LogsContribSrl


class ManContribAzimutes(APIView):
    """
    Manage Contributions positions azimutes
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes     = [JSONParser]

    def get(self, request, ctb, geom):
        """
        Retrieve azimutes of some contribution
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        geom = geom if geom == 'geom' or geom == 'geombf' else 'geom'
        M = VolunteersPositions if geom == 'geom' else VolunteersPositionsBackFront
        S = ContribPositionsSrl if geom == 'geom' else ContribPosistionsBackFrontSrl

        # Get contribution
        try:
            ctbi = VolunteersContributions.objects.get(pk=ctb)

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution does'n exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Get Azimutes
        if not _status:
            objs = M.objects.filter(cid=ctb)
            srl  = S(objs, many=True)

            code, mess = "S20", "Data successfully returned"

            response, http = {
                "status" : {"code" : code, "message" : mess},
                "data"   : srl.data
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        li = LogsContribSrl(data={
            'url'      : f'volu/ctb-azimutes/{ctb}/{geom}/',
            'service'  : 'manage-ctb-azimutes',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return r



class ManContribAzimute(APIView):
    """
    Manage Contributions positions azimutes
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes     = [JSONParser]

    def get(self, request, ctb, geom, pid):
        """
        Retrieve specific azimute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        geom = geom if geom == 'geom' or geom == 'geombf' else 'geom'
        M = VolunteersPositions if geom == 'geom' else VolunteersPositionsBackFront
        S = ContribPositionsSrl if geom == 'geom' else ContribPosistionsBackFrontSrl

        # Get Contribution position instance
        try:
            cpos = M.objects.get(cid=ctb, pid=pid)
        except M.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Contribution position instance does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = S(cpos, many=False)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        li = LogsContribSrl(data={
            'url'      : f'volu/ctb-azimute/{str(ctb)}/{geom}/{str(pid)}/',
            'service'  : 'manage-ctb-azimute',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return r
    
    def put(self, request, ctb, geom, pid):
        """
        Update Contribution azimute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        geom = geom if geom == 'geom' or geom == 'geombf' else 'geom'
        M = VolunteersPositions if geom == 'geom' else VolunteersPositionsBackFront
        S = ContribPositionsSrl if geom == 'geom' else ContribPosistionsBackFrontSrl

        # Get Contribution position instance
        try:
            cpos = M.objects.get(cid=ctb, pid=pid)

        except M.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Contribution position instance does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        if not _status and "azimute" not in d:
            _status, http = {
                "code"    : "E01",
                "message" : "Azimute not in request, nothing to do"
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            srl = S(cpos, data={
                "pid"     : cpos.pid,
                "cid"     : cpos.cid.fid,
                "geom"    : cpos.geom,
                "azimute" : d["azimute"]
            })

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Azimute was updated."
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
            
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        li = LogsContribSrl(data={
            'url'      : f'volu/ctb-azimute/{str(ctb)}/{geom}/{str(pid)}/',
            'service'  : 'manage-ctb-azimute',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["code"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return r

