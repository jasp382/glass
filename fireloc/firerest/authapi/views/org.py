"""
Organizations related Views
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

from authapi.models import Organizations
from authapi.srl import OrgSrl

from logs.srl import LogsAuthSrl


class ManOrgs(generics.GenericAPIView):
    """
    Retrieve all organizations, add new organization and
    delete all organizations
    """

    serializer_class = OrgSrl
    
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve a list with all existing Organizations
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        orgs = Organizations.objects.all()
        srl  = OrgSrl(orgs, many=True)

        code, mess = "S20", "Data successfully returned"
        
        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/org/',
            'service'  : 'manage-organizations',
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
        Method POST - Create new Organization
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, pp = request.data, ["alias", "name"]

        opt = [
            "address", 'city', 'state', 'postal',
            'country', "countryi", "phone", "email"
        ]

        _status, http = check_rqst_param(pp, list(d.keys()))

        if not _status:
            for p in opt:
                if p not in d:
                    d[p] = None
            
            srl = OrgSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : 'S21',
                    "message" : "New Organization was created"
                }, status.HTTP_201_CREATED

            else:
                errors = srl.errors

                if "slug" in errors and errors["slug"][0] \
                    == "organizations with this slug already exists.":
                    response = {"status" :{
                        "code"    : "I02",
                        "message" : "Organization with this alias already exists"
                    }}
                
                else:
                    response = {"status" : {
                        "code"    : "Z01",
                        "message" : errors
                    }}

                http = status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/org/',
            'service'  : 'manage-organizations',
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
    
    def delete(self, request):
        """
        Method DELETE - Delete all Organizations
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)


        # Get user and user type
        status, http, cuser = None, None, request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            Organizations.objects.all().delete()
            
            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Organizations deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : 'auth/org/',
            'service'  : 'manage-organizations',
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



class ManOrg(generics.GenericAPIView):
    """
    Manage Organization
    """
    
    serializer_class = Organizations
    
    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]
    
    def get(self, request, slug):
        """
        Method GET - Retireve a specific Organization
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            o = Organizations.objects.get(alias=slug)
        except Organizations.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Organization doesn't exist."
            }, status.HTTP_404_NOT_FOUND
 
        if not _status:
            srl = OrgSrl(o)

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
            'url'      : f'auth/org/{str(slug)}/',
            'service'  : 'manage-organization',
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
        Method PUT - Update a specific Organization
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = [
            "alias", "name", "address", 'city',
            'state', 'postal',
            'country', "countryi", "phone", "email"
        ]
        
        try:
            o = Organizations.objects.get(alias=slug)
            srli = OrgSrl(o)
            srldata = srli.data
        
        except Organizations.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Organization doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = srldata[p]
     
            srl = OrgSrl(o, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Organization was updated."
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
            'url'      : f'auth/org/{str(slug)}/',
            'service'  : 'manage-organization',
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
        Method DELETE - Delete a specific Organization
        ---
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http = None, None
        
        try:
            o = Organizations.objects.get(slug=slug)
        except Organizations.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Organization doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            o.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Organization deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)
            
        # Write logs
        logsrl = LogsAuthSrl(data={
            'url'      : f'auth/org/{str(slug)}/',
            'service'  : 'manage-organization',
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

