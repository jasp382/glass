"""
Users Groups related Views
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

from glass.pys import obj_to_lst

from firerest.permcls import IsFireloc

from authapi.srl import GroupsSrl
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from firerest.utils import check_rqst_param
from authapi.utils  import id_usertype

from logs.srl import LogsAuthSrl

################################################################################
# ################################# Groups #####################################
################################################################################

class GroupsManage(APIView):
    """
    Groups Management
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Groups
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        qp = request.query_params

        ctx = {
            "users" : None if "users" not in qp else True \
                if qp["users"] == "true" else None,
            "layers" : None if "layers" not in qp else True \
                if qp["layers"] == "true" else None
        }

        # Get groups objects
        groups = Group.objects.all()
        serializer = GroupsSrl(groups, many=True, context=ctx)

        code, msg = "S20", "Data successfully returned"

        # Response
        r = {
            "status" : {"code" : code, "message" : msg},
            "data"   : serializer.data
        }

        rr = Response(r, status=status.HTTP_200_OK)

        log_i = LogsAuthSrl(data={
            'url'      : 'auth/groups/',
            'service'  : 'manage-groups',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()

        return rr
    
    def post(self, request, format=None):
        """
        Create new group
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http  = None, None

        # Group data
        rd = request.data

        # Parameters
        pr = ["group"]

        _status, http = check_rqst_param(pr, list(rd.keys()))
        
        # Create new group
        if not _status:
            rd["name"] = rd["group"]
            srl = GroupsSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Group created!"
                }, status.HTTP_201_CREATED
            
            else:
                if "code='unique'" in str(srl.errors):
                    code = "I02"
                    msg = "Group already registed"
                
                else:
                    code, msg = "UNK", str(srl.errors)
                
                response, http = {
                    "status" : {"code": code, "message": msg
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}
        
        fr = Response(response, status=http)

        # Write Logs
        li = LogsAuthSrl(data={
            'url'      : 'auth/groups/',
            'service'  : 'manage-groups',
            'http'     : fr.status_code,
            'code'     : response['status']['code'],
            'message'  : response['status']['message'],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(k)}" for k in rd]),
            'method'   : request.method,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fr
    
    def delete(self, request):
        """
        Delete all groups
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        cuser = request.user
        P = id_usertype(cuser)

        if P != 'superuser':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action"
            },  status.HTTP_403_FORBIDDEN
        
        if not _status:
            Group.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Groups deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        

        fr = Response(response, status=http)

        # Write Logs
        li = LogsAuthSrl(data={
            'url'      : 'auth/groups/',
            'service'  : 'manage-groups',
            'http'     : fr.status_code,
            'code'     : response['status']['code'],
            'message'  : response['status']['message'],
            'datehour' : daytime,
            'data'     : None,
            'method'   : request.method,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fr


class GroupManage(APIView):
    """
    Specific Group Management
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, gpid):
        """
        Get Specific Group
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, qp = None, None, request.query_params

        ctx = {
            "users" : None if "users" not in qp else True \
                if qp["users"] == "true" else None,
            "layers" : None if "layers" not in qp else True \
                if qp["layers"] == "true" else None
        }

        try:
            gp = Group.objects.get(name=gpid)
            
        except Group.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Group doesn't exist"
            }, status.HTTP_400_BAD_REQUEST

        # Get Group
        if not _status:
            srl = GroupsSrl(gp, context=ctx)

            response = srl.data

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data successfully returned"
            }, status.HTTP_200_OK
            
        else:
            response = {"status" : _status}
            
        r = Response(response, http)

        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : f'auth/group/{gpid}/',
            'service'  : 'manage-groups',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response['status']["code"],
            'message'  : response['status']["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()
        
        return r

    def put(self, request, gpid):
        """
        Edit given Group
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        # Check if group exists
        try:
            gp = Group.objects.get(name=gpid)         
        except Group.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Group doesn't exist."
            }, status.HTTP_400_BAD_REQUEST

        # Check if user's exists
        if not _status and "usernames" in d and d["usernames"]:
            users = obj_to_lst(d["usernames"])
            uobj = []

            for u in users:
                try:
                    usr = User.objects.get(username=u)
                    uobj.append(usr)

                except User.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "User doesn't exist."
                    }, status.HTTP_400_BAD_REQUEST

                    break
        
        # Update group if name in request.
        if not _status:
            if "name" in d:
                srl = GroupsSrl(gp, data=d)

                if srl.is_valid():
                    srl.save()
                
                else:
                    if "code='unique'" in str(srl.errors):
                        code = "I02"
                        msg = "Group already registed"
                
                    else:
                        code, msg = "UNK", str(srl.errors)

                    _status, http = {
                        "code"    : code,
                        "message" : msg
                    }, status.HTTP_400_BAD_REQUEST
            
            else:
                srl = GroupsSrl(gp)
            
        if not _status:
            response = srl.data

            if "usernames" in d:
                for u in uobj:
                    # Get user groups
                    userg = u.groups.all()
    
                    userg[0].user_set.remove(u)
                    gp.user_set.add(u)
            
            response["status"], http = {
                "code"    : "S22",
                "message" : "Group updated!"
            }, status.HTTP_201_CREATED
  
        else:
            response = {"status" :_status}
        
        fresp = Response(response, status=http)

        # Write logs
        li = LogsAuthSrl(data={
            'url'      : f'auth/group/{gpid}/',
            'service'  : 'manage-group',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(k)}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()
        
        return fresp

    def delete(self, request, gpid, format=None):
        """
        Delete Specific Group
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, = None, None

        # Check if group exists
        try:
            gp = Group.objects.get(name=gpid)         
        except Group.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Group doesn't exist."
            }, status.HTTP_400_BAD_REQUEST

        # Delete
        if not _status:
            gp.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "User Group deleted."
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        f_resp = Response(response, status=http)

        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : f'auth/user/{gpid}/',
            'service'  : 'manage-user',
            'method'   : request.method,
            'http'     : f_resp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()

        return f_resp
        