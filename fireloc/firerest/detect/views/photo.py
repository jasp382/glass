"""
Photo Classification Endpoints
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

from firerest.utils   import check_rqst_param
from firerest.permcls import IsFireloc
from authapi.utils    import id_usertype

from detect.models import PhotoClassification, PhotoClassAttr, PhotoClassAttrValue
from detect.srl import PhotoClassSrl, PhotoClassAttrValSrl
from contrib.models import VolunteersContributions
from logs.srl import LogsFiredetectSrl


class ManPhotoClassis(APIView):
    """
    Manage Photo classification results
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Photo classification results
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        phtclass = PhotoClassification.objects.all()
        srl      = PhotoClassSrl(phtclass, many=True)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photos-class/',
            'service'  : 'photo-classification-results',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def post(self, request):
        """
        Add new Photo classification result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        pp = ["isfire", "issmoke", "ctb"]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        # check if procedure exists
        if not _status:
            try:
                c = VolunteersContributions.objects.get(fid=int(rd["ctb"]))

                rd["ctb"] = c.fid
            
            except VolunteersContributions.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : f"Contribution {rd['ctb']} doesn't exist."
                }, status.HTTP_400_BAD_REQUEST

        #extra attrs
        pp.append("pic")
        exattr = [k for k in rd if k not in pp]
        attrs = []
        if not _status:
            for a in exattr:
                try:
                    #get Photo classification result extra attrs
                    phtattr = PhotoClassAttr.objects.get(slug=a)
                    attrs.append(phtattr)
                
                except PhotoClassAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Attribute '{a}' doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break

        # Record new Photo classification result
        if not _status:
            srl = PhotoClassSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST 
          
        ed = []
        # Record extra attrs and their values
        if not _status:
            for e in range(len(exattr)):                
                #attr object
                aobj = attrs[e]

                ed.append({
                    'pcattr'   : aobj.id,
                    'photocls' : response['id'],
                    'value'    : rd[exattr[e]]
                })
                        
            sattr = PhotoClassAttrValSrl(data=ed, many=True)

            if sattr.is_valid():
                sattr.save()
  
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New FLoc Photo classification result created."
                }, status.HTTP_201_CREATED
                
            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(sattr.errors)
                }, status.HTTP_400_BAD_REQUEST
            
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photos-class/',
            'service'  : 'photo-classification-results',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request):
        """
        Delete all results
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser, _status, http = request.user, None, None
        ustype = id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            PhotoClassification.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "FLoc Photo classification results deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photos-class/',
            'service'  : 'photo-classification-results',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr


class ManPhotoClass(APIView):
    """
    Manage FLoc Photo classification result
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, photoid):
        """
        Get Specific Photo classification result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            phtclass = PhotoClassification.objects.get(pk=photoid)
        except PhotoClassification.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Photo classification result doesn't exist."
            }, status.HTTP_404_NOT_FOUND


        if not _status:
            srl = PhotoClassSrl(phtclass)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/photo-class/{photoid}/',
            'service'  : 'photo-classification-result',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def put(self, request, photoid):
        """
        Update Photo classification result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["isfire", 'prcd']

        #Extra Attr
        extattr = [k for k in d if k not in rp]

        try:
            phtclass = PhotoClassification.objects.get(pk=photoid)
            pcsrl    = PhotoClassSrl(phtclass)
            pcdata   = pcsrl.data
        except PhotoClassification.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "FLoc Photo classification result doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = pcdata[p]
        
        # Get extra attributes
        attrobj = []
        if not _status and len(extattr):
            for attr in extattr:
                try:
                    pcattr = PhotoClassAttr.objects.get(slug=attr)
                    attrobj.append(pcattr)
                
                except PhotoClassAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "FLoc Photo Classification Attribute doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
        
        # Update instance
        if not _status:
            srl = PhotoClassSrl(phtclass, data=d)
            if srl.is_valid():
                srl.save()
            
            else:
                _status, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        #Handle PhotoClassAttr
        srl_attr = []
        if not _status and len(attrobj):
            for attr in attrobj:
                _d = {
                    'pcattr'   : attr.id,
                    'photocls' : phtclass.id,
                    'value'    : d[attr.slug]
                }

                try: 
                    attrval = PhotoClassAttrValue.objects.get(
                        pcattr=attr.id, photocls=phtclass.id
                    )
                    
                    attrsrl = PhotoClassAttrValSrl(attrval, data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                
                except PhotoClassAttrValue.DoesNotExist:
                    # Add new value
                    attrsrl = PhotoClassAttrValSrl(data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                
                except PhotoClassAttrValue.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "E09",
                        "message" : "This photcls has more than one value for one attr"
                    }, status.HTTP_400_BAD_REQUEST
                    
        if not _status:
            response = srl.data

            if len(srl_attr):
                response["attr"] = srl_attr

            response["status"], http = {
                "code"    : "S22",
                "message" : "FLoc Photo classification result was updated."
            }, status.HTTP_201_CREATED

        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/photo-class/{photoid}/',
            'service'  : 'photo-classification-result',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, photoid):
        """
        Delete one result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            phtclass = PhotoClassification.objects.get(pk=photoid)
        except PhotoClassification.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "FLoc Photo classification result doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            phtclass.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "FLoc Photo classification result deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/photo-class/{photoid}/',
            'service'  : 'photo-classification-result',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr

