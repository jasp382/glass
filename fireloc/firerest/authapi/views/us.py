"""
Views to users management
"""

import datetime as dt

import pytz

from django.contrib.auth.hashers import make_password

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from firerest.permcls  import IsFireloc

from firerest.utils import check_rqst_param
from authapi.utils  import id_usertype

from django.contrib.auth.models import User, Group
from authapi.models             import UserAttr, UserAttrValue
from authapi.srl                import UserAttrValueSrl, UserSrl

from logs.srl import LogsAuthSrl

################################################################################
# ################################## Users ################################### #
################################################################################


class ManUsers(APIView):

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        List Users registed in the System

        Allow filter by group
        """

        import pandas as pd
        from collections import OrderedDict

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get Query Params
        qp = request.query_params

        # ID Group
        if "groups" in qp:
            groups = qp["groups"].split(',')

            users = User.objects.filter(groups__name__in=groups)
        
        else:
            users = User.objects.all()
        
        serializer = UserSrl(users, many=True)

        # Delete password from serializer data
        if not serializer.data:
            data = serializer.data
        else:
            users_df = pd.DataFrame(serializer.data)
            users_df.drop(['password'], axis=1, inplace=True)
            data = users_df.to_dict(orient='records', into=OrderedDict)
        
        # Response objects
        code, msg = "S20",  "Data successfully returned" 
        rsp = {
            "status" : {"code": code, "message" : msg},
            "data"   : data
        }

        r = Response(rsp, status=status.HTTP_200_OK)
        
        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : 'auth/users/',
            'service'  : 'manage-users',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : ";".join([
                f"{str(k)}={str(qp[k])}" for k in qp
            ]) if "groups" in qp else None,
            'cuser'    : request.user.pk
        })

        if log_i.is_valid(): log_i.save()

        return r
    
    def post(self, request):
        """
        Method POST - Create not regular users
        (eg. Fireloc users or RiskManager users
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d = request.data

        # Mandatory parameters
        rp = ["email", "password", "first_name", "last_name", "group"]

        # Check if we have all mandatory parameters in the request.data
        _status, http = check_rqst_param(rp, list(d.keys()))

        # Check if group exists
        if not _status:
            try:
                grp = Group.objects.get(name=d["group"])
            except Group.DoesNotExist:
                _status, http = {
                "code"    : "I03",
                "message" : "Group doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Get user extra attributes
        exattr = [k for k in d if k not in rp]
        attrs = []
        if not _status:
            for a in exattr:
                try:
                    aobj = UserAttr.objects.get(slug=a)
                    attrs.append(aobj)
                except UserAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Attribute doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break
        
        # Record User
        if not _status:
            # Get username
            d["username"] = d["email"]

            # User Serializer
            srl = UserSrl(data=d)

            if srl.is_valid():
                srl.save()

                # Add user to GROUP
                nus = User.objects.get(username=d["username"])
                grp.user_set.add(nus)

            else:
                errors = str(srl.errors)

                if "username" in errors:
                    _status = {
                        "code"    : "I02",
                        "message" : "User already registed"
                    }
                
                else:
                    _status = {
                        "code"    : "Z01",
                        "message" : errors
                    }
                
                http = status.HTTP_400_BAD_REQUEST
        
        # Record extra attributes and respective values
        attrval = []
        if not _status:
            for e in range(len(exattr)):
                attrval.append({
                    'attr'  : attrs[e].id,
                    'user'  : nus.id,
                    'value' : d[exattr[e]]
                })
            
            sattr = UserAttrValueSrl(data=attrval, many=True)

            if sattr.is_valid():
                sattr.save()
                
            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(sattr.erors)
                }, status.HTTP_400_BAD_REQUEST
        
        # Todo: del user if add attr ended with error
        
        # Get response data
        if not _status:
            response = srl.data

            if len(attrval):
                response["attr"] = sattr.data

            del response['password']

            response["status"], http = {
                "code"    : 'S21',
                "message" : "New user was created"
            }, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}

        # Final response
        fr = Response(response, status=http)

        # Write Logs
        lsrl = LogsAuthSrl(data={
            'url'      : 'auth/users',
            'service'  : 'manage-users',
            'method'   : request.method,
            'http'     : fr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ';'.join([
                f'{k}={str(d[k])}' for k in d if k != 'password'
            ]),
            'cuser'    : request.user.pk
        })

        if lsrl.is_valid(): lsrl.save()

        return fr
    
    def delete(self, request):
        """
        Delete all Users
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        cuser = request.user
        P = id_usertype(cuser)

        qp = request.query_params

        if P != 'superuser':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action"
            },  status.HTTP_403_FORBIDDEN

        if not _status:
            if "groups" in qp:
                groups = qp["groups"].split(',')

                users = User.objects.filter(groups__name__in=groups)
        
            else:
                users = User.objects.filter(is_superuser=False)
            
            users.delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Users deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : 'auth/users/',
            'service'  : 'manage-users',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{str(k)}={str(qp[k])}" for k in qp
            ]) if "groups" in qp else None,
            'cuser'    : cuser.pk
        })

        if log_i.is_valid(): log_i.save()

        return rr


class CreateJustAUser(APIView):
    """
    Create a User of the group JustAUser
    """

    parser_classes = [JSONParser]

    def post(self, request):
        """
        Create Regular User
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        params = ["email", "password"]

        d = request.data

        exattr = [
            k for k in d if k not in params and \
                k != 'first_name' and k != 'last_name' \
                    and k != 'group' and d[k]
        ]

        # Check if parameters are valid
        _status, http = check_rqst_param(params, list(d.keys()))
        
        # Get user extra attributes
        attrs = []
        if not _status:
            for a in exattr:
                try:
                    aobj = UserAttr.objects.get(slug=a)
                    attrs.append(aobj)
                except UserAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Attribute doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break

        # Record User
        if not _status:
            # Get Username
            d["username"] = d["email"]

            # Get First Name and Last Name
            d["first_name"] = d.get('first_name', 'None')
            d["last_name"]  = d.get('last_name', 'None')
            
            # Get User serializer
            srl = UserSrl(data=d)

            if srl.is_valid():
                srl.save()

                # Add user to GROUP
                crt_user = User.objects.get(username=d["username"])
                grp = Group.objects.get(name='justauser') 
                grp.user_set.add(crt_user)
        
            else:
                errors = srl.errors

                if 'username' in errors:
                    _status = {
                        "code"    : 'I02',
                        "message" : "User already registed"
                    }
                
                else:
                    _status = {
                        "code"    : 'Z01',
                        "message" : str(errors)
                    }

                http = status.HTTP_400_BAD_REQUEST
        
        # Record extra attributes and their values
        if not _status:
            for e in range(len(exattr)):
                aobj = attrs[e]

                sattr = UserAttrValueSrl(data={
                    'attr'  : aobj.id,
                    'user'  : crt_user.id,
                    'value' : d[exattr[e]]
                })

                if sattr.is_valid():
                    sattr.save()
                
                else:
                    _status, http = {
                        "code" : "Z01",
                        "message" : str(sattr.errors)
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Todo: del user if add attr ended with error

        # Get response
        if not _status:
            response = srl.data

            del response["password"]

            response["status"], http = {
                "code"    : 'S21',
                "message" : "New user was created"
            }, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        f_response = Response(response, status=http)

        # Write Logs
        logs_i = LogsAuthSrl(data={
            'url'      : 'auth/justauser/',
            'service'  : 'add-regular-user',
            'http'     : f_response.status_code,
            'code'     : response["status"]['code'],
            'message'  : response["status"]['message'],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(d[k])}" for k in d if k != 'password'
            ]),
            'method'   : request.method,
            'cuser'    : None
        })

        if logs_i.is_valid(): logs_i.save()

        # Return response
        return f_response


class ManUser(APIView):
    """
    Get Users Details
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]
    
    def get(self, request, userid):
        """
        Get Details of One User
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, _return = None, None, None

        # Get current user and user type
        cuser = request.user
        P = id_usertype(cuser)

        # Get userid
        if userid == 'thisuser':
            userid = cuser.email

        # Get User
        try:
            user = User.objects.get(username=userid)
        
        except User.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "User doesn't exist"
            }, status.HTTP_400_BAD_REQUEST

        # Check Privileges
        if not _status:
            if P == 'superuser' or P == 'fireloc':
                _return = 1
            
            else:
                if user.id == cuser.id:
                    _return = 1
            
            if not _return:
                _status, http = {
                    "code"    : "E03",
                    "message" : "You do not have permission to perform this action."
                }, status.HTTP_403_FORBIDDEN

        # Get User
        if not _status:
            srl = UserSrl(user)

            response = srl.data

            del response['password']

            response["status"], http = {
                "code"    : "S20",
                "message" : "Data successfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        f_response = Response(response, http)

        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : 'auth/user/',
            'service'  : 'manage-user',
            'method'   : request.method,
            'http'     : f_response.status_code,
            'code'     : response['status']["code"],
            'message'  : response['status']["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if log_i.is_valid(): log_i.save()

        return f_response
    
    def put(self, request, userid):
        """
        Edit given User
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        # Get User
        cuser  = request.user
        ustype = id_usertype(cuser)

        # Get user id
        if userid == 'thisuser':
            userid = cuser.email
        
        # Request parameters
        params = ['password', 'email', 'first_name', 'last_name'] 

        #get the extra params
        extattr = [k for k in d if k not in params and k != 'group']

        if cuser.username != userid and ustype != 'superuser' and ustype != 'fireloc':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_403_FORBIDDEN
        
        if not _status:
            try:
                usr = User.objects.get(username=userid)
                srl = UserSrl(usr)
                srldata = srl.data
            
            except User.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "User doesn't exist"
                }, status.HTTP_404_NOT_FOUND
        
        eattr = []  
        # Check if user attributes are valid
        if not _status and len(extattr):
            for attr in extattr:
                # Check if attr exists
                try:
                    attrobj = UserAttr.objects.get(slug=attr)

                    eattr.append(attrobj)
                
                except UserAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"{attr} doesn't exist"
                    }, status.HTTP_404_NOT_FOUND
                
                if _status:
                    break
        
        # Check if we have group
        if not _status and "group" in d:
            try:
                gp = Group.objects.get(name=d["group"])

                userg = usr.groups.all()

                userg[0].user_set.remove(usr)
                gp.user_set.add(usr)
            
            except Group.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Group doesn't exist"
                }, status.HTTP_400_BAD_REQUEST

        if not _status: 
            for p in params:
                if p == 'password' and p in d:
                    d[p] = make_password(d[p])
                    continue
                
                if p not in d:
                    d[p] = srldata[p]

            # Update User
            d["username"] = d["email"]
            srl = UserSrl(usr, data=d)       

            if not srl.is_valid():
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }, status.HTTP_400_BAD_REQUEST
            else:
                srl.save()
        
        # Add user attributes
        srl_attr = []
        if not _status and len(eattr):
            # Get user attr value
            for attr in eattr:
                _d = {
                    'attr' : attr.id, 'user' : usr.id,
                    'value' : d[attr.slug]
                }

                try:
                    usattrval = UserAttrValue.objects.get(
                        attr=attr.id, user=usr.id
                    )

                    attrsrl = UserAttrValueSrl(usattrval, data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                
                except UserAttrValue.DoesNotExist:
                    # no value associated
                    # Create new value
                    attrsrl = UserAttrValueSrl(data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                
                except UserAttrValue.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "I04",
                        "message" : "One User has more than one value for one attr"
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        if not _status:
            nsrl = UserSrl(usr)
            response = nsrl.data
            
            response["status"], http = {
                "code"    : "S22",
                "message" : "User edited"
            }, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)

        # Write logs
        li = LogsAuthSrl(data={
            'url'      : f'auth/user/{userid}/',
            'service'  : 'manage-user',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(d[k])}" for k in d if k != 'password'
            ]),
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fresp
    
    def delete(self, request, userid):
        """
        Delete User
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Check privileges
        cuser = request.user
        P = id_usertype(cuser)

        if userid == 'thisuser':
            userid = cuser.email

        try:
            user = User.objects.get(username=userid)

            ustype = id_usertype(user)
        
        except User.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "User doesn't exist"
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            # Check if current user can delete given user
            del_ = None
            if P == 'superuser' and ustype != 'superuser':
                user.delete()
                del_ = 1
            
            elif P == 'fireloc':
                if ustype != 'fireloc' and ustype != 'superuser':
                    user.delete()
                    del_ = 1
            
            else:
                if cuser.id == user.id:
                    user.delete()
                    del_ = 1
            
            response = {"status" : {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }} if not del_ else {"status" : {
                "code"    : "S23",
                "message" : "User deleted"
            }}

            http = status.HTTP_200_OK if del_ else status.HTTP_403_FORBIDDEN
        
        else:
            response = {"status" : _status}

        f_resp = Response(response, status=http)

        # Write Logs
        log_i = LogsAuthSrl(data={
            'url'      : f'auth/user/{userid}/',
            'service'  : 'manage-user',
            'method'   : request.method,
            'http'     : f_resp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if log_i.is_valid(): log_i.save()

        return f_resp

