"""
Fire Location Assessment and Photo classification Attributes
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
from detect.models    import FirelocAttr
from detect.models    import PhotoClassAttr

from detect.srl import FirelocAttrSrl, PhotoClassAttrSrl

from logs.srl import LogsFiredetectSrl


class FirelocAttrs(APIView):
    """
    Manage Fire location attributes
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Fire location assessment attributes
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        attrs = FirelocAttr.objects.all()
        srl   = FirelocAttrSrl(attrs, many=True)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-attrs/',
            'service'  : 'manage-fireloc-attrs',
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
        Method POST - Add new Fire location assessment attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        pp = ["slug", "name", "dtype"]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        if not _status:
            srl = FirelocAttrSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New FLoc attribute created."
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST 

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-attrs/',
            'service'  : 'manage-fireloc-attrs',
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
    
    def delete(self, request, format=None):
        """
        Delete all FLoc attributes
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        cuser, _status, http = request.user, None, None
        ustype= id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            FirelocAttr.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "FireLoc Attributes deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}


        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-attrs/',
            'service'  : 'manage-fireloc-attrs',
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


class MFirelocAttr(APIView):
    """
    Manage Fire location attribute
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, slug):
        """
        Method GET - Retireve a specific Attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = FirelocAttr.objects.get(slug=slug)
        except FirelocAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND


        if not _status:
            srl = FirelocAttrSrl(attr)

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
            'url'      : f'floc/floc-attr/{str(slug)}/',
            'service'  : 'manage-fireloc-attr',
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
    
    def put(self, request, slug):
        """
        Update an attribute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["slug", 'name', 'dtype']

        try:
            attr  = FirelocAttr.objects.get(slug=slug)
            asrl  = FirelocAttrSrl(attr)
            asrld = asrl.data
        
        except FirelocAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "FLocAttribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = asrld[p]
     
            srl = FirelocAttrSrl(attr, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "FLoc Attribute was updated."
                }, status.HTTP_201_CREATED
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-attr/{str(slug)}/',
            'service'  : 'manage-fireloc-attr',
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
    
    def delete(self, request, slug, format=None):
        """
        Delete attribute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = FirelocAttr.objects.get(slug=slug)
        except FirelocAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Attribute deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
 
        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-attr/{str(slug)}/',
            'service'  : 'manage-user-attr',
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


class PhotocAttrs(APIView):
    """
    Manage Photo classification attributes
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Photo Classification attributes
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)


        attrs = PhotoClassAttr.objects.all()
        srl   = PhotoClassAttrSrl(attrs, many=True)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photocls-attrs/',
            'service'  : 'manage-photo-class-attrs',
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
        Add new Photo classification attribute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd = request.data

        pp = ["slug","name", "dtype"]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        if not _status:
            srl = PhotoClassAttrSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Photo Classification attribute created."
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST 

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photocls-attrs/',
            'service'  : 'manage-photo-class-attrs',
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
    
    def delete(self, request, format=None):
        """
        Delete all attributes
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
            PhotoClassAttr.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Photo Classification Attributes deleted"
            }},status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/photocls-attrs/',
            'service'  : 'manage-photo-class-attrs',
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


class PhotoAttr(APIView):
    """
    Manage Photo Classification attribute
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, slug):
        """
        Get a single attribute
        """
     
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = PhotoClassAttr.objects.get(slug=slug)
        except PhotoClassAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND


        if not _status:
            srl = PhotoClassAttrSrl(attr)

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
            'url'      : f'floc/photocls-attr/{str(slug)}/',
            'service'  : 'manage-photo-class-attr',
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
    
    def put(self, request, slug, format=None):
        """
        Method PUT - Update an attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["slug", 'name', 'dtype']

        try:
            attr  = PhotoClassAttr.objects.get(slug=slug)
            asrl  = PhotoClassAttrSrl(attr)
            asrld = asrl.data
        
        except PhotoClassAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Photo Classification Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = asrld[p]
     
            srl = PhotoClassAttrSrl(attr, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Photo Classification Attribute was updated."
                }, status.HTTP_201_CREATED
            
            else:
                _status, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/photocls-attr/{str(slug)}/',
            'service'  : 'manage-photo-class-attr',
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
    
    def delete(self, request, slug):
        """
        Delete attribute
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = PhotoClassAttr.objects.get(slug=slug)
        except PhotoClassAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Photo Classification Attribute deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
 
        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/photocls-attr/{str(slug)}/',
            'service'  : 'manage-user-attr',
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

