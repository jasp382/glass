"""
UsersAttr related Views
"""

import datetime as dt
import pytz

# REST Framework Dependencies
from rest_framework.response import Response
from rest_framework          import status
from rest_framework          import permissions
from rest_framework.parsers  import JSONParser
from rest_framework          import generics

from drf_yasg.utils import swagger_auto_schema

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls import IsFireloc
from firerest.utils   import check_rqst_param
from authapi.utils    import id_usertype

from authapi.models import UserAttr
from authapi.srl import UserAttrSrl

from logs.srl import LogsAuthSrl

################################################################################
#################################### Use Attrs #################################
################################################################################


class ManUserAttrs(generics.GenericAPIView):
    """
    GET - List all attributes
    POST - Create attribute
    """
    
    serializer_class = UserAttrSrl
    
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request):
        """
        Method GET - Retrieve a list with all existing User Attrbiutes
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        attrs = UserAttr.objects.all()
        serializer = UserAttrSrl(attrs, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : serializer.data
        }, status=status.HTTP_200_OK)
        
        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/attrs/',
            'service'  : 'manage-user-attrs',
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
        Method POST - Create a User Attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        d, pp = request.data, ["name", "slug", "atype"]

        _status, http = check_rqst_param(pp, list(d.keys()))

        if not _status:
            d["atype"] = "str" if d["atype"] != "int" and \
                d["atype"] != "str" and d["atype"] != "float" and \
                    d["atype"] != "bool" else d["atype"]
            
            srl = UserAttrSrl(data=d)
            
            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New attribute created."
                }, status.HTTP_201_CREATED
                
            else:
                if "code='unique'" in str(srl.errors):
                    code = "I02"
                    msg = "Attribute already exists"
                
                else:
                    code, msg = "Z01", str(srl.errors)

                response, http = {"status" : {
                    "code"    : code, 
                    "message" : msg
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/attrs/',
            'service'  : 'manage-user-attrs',
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
    
    @swagger_auto_schema(responses={200: "User Attributes deleted"})
    def delete(self, request):
        """
        Method DELETE - Delete all User attributes
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)


        # Get user and user type
        status, http, cuser = None, None, request.user
        ustype, _status = id_usertype(cuser)

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            UserAttr.objects.all().delete()
            
            response, http = {"status" : {
                "code"    : "S24",
                "message" : "User Attributes deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/attrs/',
            'service'  : 'manage-user-attrs',
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


class ManUserAttr(generics.GenericAPIView):
    """
    GET - Get a specific attribute
    PUT - Update a specific attribute
    DELETE - Delete a specific attribute
    """
    
    serializer_class = UserAttrSrl
    
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request, slug):
        """
        Method GET - Retireve a specific User Attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            attr = UserAttr.objects.get(slug=slug)
        except UserAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
 
        if not _status:
            srl = UserAttrSrl(attr)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : f'auth/attr/{str(slug)}/',
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
    
    def put(self, request, slug):
        """
        Method PUT - Update a specific User Attribute
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = ["slug", 'name', 'atype']
        
        try:
            attr = UserAttr.objects.get(slug=slug)
            srli = UserAttrSrl(attr)
            srldata = srli.data
        
        except UserAttr.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Attribute doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
     
            srl = UserAttrSrl(attr, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Attribute was updated."
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
        logsrl = LogsAuthSrl(data={
            'url'      : f'auth/attr/{str(slug)}/',
            'service'  : 'manage-user-attr',
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
            
    @swagger_auto_schema(responses={200: "Attribute deleted"})
    def delete(self, request, slug):
        """
        Method DELETE - Delete a specific User Attribute
        ---
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            attr = UserAttr.objects.get(slug=slug)
        except UserAttr.DoesNotExist:
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
        logsrl = LogsAuthSrl(data={
            'url'      : f'auth/attr/{str(slug)}/',
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
