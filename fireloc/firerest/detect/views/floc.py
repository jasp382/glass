"""
Fire Location Assessment Endpoints
"""

import datetime as dt
import pytz
from osgeo import ogr
import os

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import wkt_sanitize

from firerest.settings import GEOMEDIA_FOLDERS
from firerest.utils    import check_rqst_param
from firerest.permcls  import IsFireloc
from authapi.utils     import id_usertype
from detect.models     import FirelocApproach, FirelocAssessment
from detect.models     import FirelocAttr
from detect.models     import FirelocAttrValue
from georef.models     import Places, Freguesias
from contrib.models    import VolunteersContributions
from detect.srl        import FirelocAssesSrl, FlocAttrValSrl, ReadFlocAssesSrl
from geovis.models     import MapFireAss

from logs.srl import LogsFiredetectSrl


class ManFlocAssess(APIView):
    """
    Manage Fire Location Assessment results
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - List Fire location assessment results
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rq = request.query_params

        ctx = {
            "ctb" : None if "contribs" not in rq else \
                True if rq["contribs"] == 'true' else None,
            "epsg" : None if "epsg" not in rq else int(rq["epsg"]),
            "geom" : True if "geom" in rq and rq["geom"] == "true" else None,
            "extent" : True if "extent" in rq and rq["extent"] == "true" else None,
            "cctb" : None if "countcontribs" not in rq else \
                True if rq["countcontribs"] == 'true' else None
        }

        if "step" in rq:
            objs = FirelocAssessment.objects.filter(step=int(rq["step"]))
        
        else:
            objs = FirelocAssessment.objects.all()
        

        srl  = ReadFlocAssesSrl(objs, many=True, context=ctx)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'fireloc/',
            'service'  : 'manage-fireloc-results',
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
        Method POST - Add new Fire location assessment result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rd, cuser = request.data, request.user

        ustype = id_usertype(cuser)

        #primary attrs
        pp = [
            "ctbstart", "ctbend", "aprch", "timezone",
            "extent", "epsg", "geom", "prid"
        ]

        _status, http = check_rqst_param(pp, list(rd.keys()))

        pp.extend(["startime", "endtime", "nearplace", "fregid", "step"])

        # Check user type
        if not _status and ustype != 'superuser' and ustype != 'fireloc':
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST

        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if rd["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Check if starttime and endtime values are valid
            for time in ["ctbend", "ctbstart", "startime", "endtime"]:
                if time not in rd: continue

                try:
                    tt = dt.datetime.strptime(rd[time], '%Y-%m-%d %H:%M:%S')

                    _tz = pytz.timezone(rd["timezone"])

                    rd[time] = _tz.localize(tt)
                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"{time} has not the right format"
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break

        #check if freguesia exists
        if not _status and "fregid" in rd:
            try:
                freg = Freguesias.objects.get(code=rd["fregid"])
                rd["fregid"] = freg.id
                
            except Freguesias.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Freguesia {rd['fregid']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        else:
            rd["fregid"] = None
        
        # Check if place exist
        if not _status and "nearplace" in rd:
            try:
                pid = Places.objects.get(pk=rd["nearplace"])
                
            except Places.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Place {rd['nearplace']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        else:
            rd["nearplace"] = None
        
        # Check if approach exists
        if not _status:
            try:
                aprch = FirelocApproach.objects.get(slug=rd["aprch"])
                rd["aprch"] = aprch.id
            
            except FirelocApproach.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Approach doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        # Sanitize geometries
        if not _status:
            for g in ["geom", "extent"]:
                try:
                    rd[g] = wkt_sanitize(
                        rd[g], rgeos=True,
                        epsg = 3763 if rd["epsg"] == 3763 else rd["epsg"],
                        reprj= None if rd["epsg"] == 3763 else 3763
                    )
                
                except:
                    _status, http = {
                        "code"    : "G02",
                        "message" : "EPSG is not a Coordinate Reference System."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break

        #extra attrs
        exattr = [k for k in rd if k not in pp]
        attrs = []
        if not _status:
            for a in exattr:
                try:
                    #get floc assesm extra attrs
                    flocobj = FirelocAttr.objects.get(slug=a)
                    attrs.append(flocobj)
                except FirelocAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : f"Attribute '{a}' doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break

        #Record new floc assessment
        if not _status:
            if "step" not in rd:
                rd["step"] = 0
            
            srl = FirelocAssesSrl(data=rd)

            if srl.is_valid():
                srl.save()

                response = srl.data

            else:
                _status, http = {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }, status.HTTP_400_BAD_REQUEST
            
        # Record extra attrs and their values
        ed = []
        warns = []
        fail_epsg = None
        ispnt = 0
        if not _status:
            for e in range(len(exattr)):                
                #attr object
                aobj = attrs[e]

                if aobj.dtype == "geometry":
                    if fail_epsg: continue

                    if "epsg" not in rd:
                        warns.append((
                            "Geometries weren't added "
                            "because EPSG code is not in the "
                            "request data"
                        ))

                        fail_epsg = 1

                        continue

                    geom = wkt_sanitize(
                        rd[exattr[e]],
                        epsg=3763 if rd["epsg"] == 3763 else rd["epsg"],
                        reprj=None if rd["epsg"] == 3763 else 3763,
                        rgeos=True
                    )

                    if not geom:
                        warns.append(f"Geometry of {exattr[e]} is not valid")

                        continue

                    # Get Geometry type
                    g = ogr.CreateGeometryFromWkt(rd[exattr[e]])
                    gname = g.GetGeometryName()
                    if gname != 'POINT' and gname != "POLYGON":
                        warns.append(f"Geometry of {exattr[e]} is not a point or a polygon")

                        continue

                    ispnt = 1 if gname == 'POINT' else 0

                    rd[exattr[e]] = geom
                
                ed.append({
                    'fattr'     : aobj.id,
                    'floc'      : response['id'],
                    'value'     : None if aobj.dtype == "geometry" else rd[exattr[e]],
                    'pointgeom' : rd[exattr[e]] if aobj.dtype == "geometry" and ispnt else None,
                    'polygeom'  : rd[exattr[e]] if aobj.dtype == "geometry" and not ispnt else None

                })
            
            if ed:
                sattr = FlocAttrValSrl(data=ed, many=True)

                if sattr.is_valid():
                    sattr.save()

                    response["status"], http = {
                        "code"     : "S21",
                        "message"  : "New FLoc assessment result created.",
                        "warnings" : warns
                    }, status.HTTP_201_CREATED

                    response["attr"] = sattr.data
                
                else:
                    response, http = {"status" : {
                        "code"    : "Z01",
                        "message" : str(sattr.errors)
                    }}, status.HTTP_400_BAD_REQUEST
            
            else:
                response["status"], http = {
                    "code"      : "S21",
                    "message"   : "New FLoc assessment result created.",
                     "warnings" : warns
                }, status.HTTP_201_CREATED

        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'fireloc/',
            'service'  : 'manage-fireloc-results',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(rd[k])}" for k in rd]),
            'cuser'    : cuser.pk
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
            FirelocAssessment.objects.all().delete()

            response, http = {"status" : {
                "code"    : "S24",
                "message" : "FLoc results deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'fireloc/',
            'service'  : 'manage-fireloc-results',
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


class ManFlocResult(APIView):
    """
    Manage Fire Location Result
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes = [JSONParser]

    def get(self, request, flocid):
        """
        Get one Result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        rq = request.query_params

        ctx = {
            "ctb" : None if "contribs" not in rq else \
                True if rq["contribs"] == 'true' else None,
            "epsg" : None if "epsg" not in rq else int(rq["epsg"]),
            "geom" : True if "geom" in rq and rq["geom"] == "true" else None,
            "extent" : True if "extent" in rq and rq["extent"] == "true" else None
        }

        try:
            assm = FirelocAssessment.objects.get(pk=flocid)
        except FirelocAssessment.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Assessment Result doesn't exist."
            }, status.HTTP_404_NOT_FOUND


        if not _status:
            srl = ReadFlocAssesSrl(assm, context=ctx)

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
            'url'      : f'floc/fireloc-i/{flocid}/',
            'service'  : 'manage-fireloc-result',
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
    
    def put(self, request, flocid):
        """
        Update result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        _status, http, d = None, None, request.data

        rp = [
            'startime', 'endtime', "nearplace", "fregid",
            "step", "ctbstart", "ctbend", 
            "aprch", "extent", "prid"
        ]

        warns, tmcols = [], ["ctbend", "ctbstart", "startime", "endtime"]

        extattr = [k for k in d if k not in rp and k != 'epsg' \
            and k != 'timezone']


        if "startime" in d or "endtime" in d or "ctbstart" in d \
            or "ctbend" in d:
            if "timezone" not in d:
                warns.append(
                    'datetimes will not be updated - timezone is missing'
                )
            
            else:
                tzs = list(pytz.all_timezones)

                if d["timezone"] not in tzs:
                    _status, http = {
                        "code"    : "E08",
                        "message" : "timezone is invalid"
                    }, status.HTTP_400_BAD_REQUEST

        if not _status:
            try:
                assm  = FirelocAssessment.objects.get(pk=flocid)
                fasrl = FirelocAssesSrl(assm)
                fadat = fasrl.data
            
            except FirelocAssessment.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "FLoc Assessment Result doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        if not _status:
            for p in rp:
                if p not in d:
                    d[p] = fadat[p]
                    continue
                
                if p == 'aprch':
                    try:
                        aprch = FirelocApproach.objects.get(slug=d[p])
                        d[p] = aprch.id
                    
                    except FirelocApproach.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "Approach doesn't exist"
                        }, status.HTTP_404_NOT_FOUND
                    
                    if _status: break

                if p == 'nearplace':
                    try:
                        place = Places.objects.get(pk=d[p])
                        d[p] = place.fid
                    
                    except Places.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "Place doesn't exist"
                        }, status.HTTP_404_NOT_FOUND
                    
                    if _status: break

                if p == 'fregid':
                    try:
                        freg = Freguesias.objects.get(code=d["fregid"])
                        d["fregid"] = freg.fid
                
                    except Freguesias.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : f"Freguesia {d['fregid']} doesn't exist."
                        }, status.HTTP_404_NOT_FOUND
                    
                    if _status: break
                
                if p in tmcols:
                    try:
                        tt = dt.datetime.strptime(d[p], '%Y-%m-%d %H:%M:%S')

                        _tz = pytz.timezone(d["timezone"])

                        d[p] = _tz.localize(tt)
                    except:
                        _status, http = {
                            "code"    : "E07",
                            "message" :  f"{p} has not the right format"
                        }, status.HTTP_400_BAD_REQUEST
                
                    if _status: break

        #Update Fireloc Assesment result
        if not _status:
            srl = FirelocAssesSrl(assm, data=d)
            
            if srl.is_valid():
                srl.save()
         
            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }, status.HTTP_400_BAD_REQUEST

        # Get extra attributes
        attrobj = []
        if not _status and len(extattr):
            #Get FireLoc Attr value
            for attr in extattr:
                try:
                    flocattr = FirelocAttr.objects.get(slug=attr)

                    attrobj.append(flocattr)
                
                except FirelocAttr.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "FLoc Assessment Attribute doesn't exist."
                    }, status.HTTP_404_NOT_FOUND

        # Update extra attr
        fail_epsg = None
        srl_attr = []
        if not _status and len(attrobj):
            for attr in attrobj:
                # Sanitize Geometry
                if attr.dtype == "geometry":
                    if fail_epsg: continue

                    if "epsg" not in d:
                        warns.append((
                            "Geometries weren't added "
                            "because EPSG code is not in the "
                            "request data"
                        ))

                        fail_epsg = 1

                        continue

                    geom = wkt_sanitize(
                        d[attr.slug],
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj=None if d["epsg"] == 3763 else 3763,
                        rgeos=True
                    )

                    if not geom:
                        warns.append(f"Geometry of {attr.slug} is not valid")

                        continue
                
                    # Get Geometry type
                    g = ogr.CreateGeometryFromWkt(geom)
                    gname = g.GetGeometryName()

                    if gname != 'POINT' and gname != "POLYGON":
                        warns.append(f"Geometry of {attr.slug} is not a point or a polygon")

                        continue

                    ispnt = 1 if gname == 'POINT' else 0

                    d[attr.slug] = geom
                
                _d = {
                    'fattr' : attr.id,
                    'floc'  : assm.id,
                    'value' : d[attr.slug] if attr.dtype != 'geometry' else None,
                    'pointgeom' : d[attr.slug] if attr.dtype == 'geometry' and ispnt else None,
                    'polygeom'  : d[attr.slug] if attr.dtype == 'geometry' and not ispnt else None
                }
                
                try:
                    attrval = FirelocAttrValue.objects.get(
                        fattr=attr.id, floc=assm.id
                    )

                    attrsrl = FlocAttrValSrl(attrval, data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                    
                except FirelocAttrValue.DoesNotExist:
                    # no value associated
                    # Add new value
                    attrsrl = FlocAttrValSrl(data=_d)

                    if attrsrl.is_valid():
                        attrsrl.save()

                        srl_attr.append(attrsrl.data)
                    
                except FirelocAttrValue.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "E03",
                        "message" : "This flocassess has more than one value for one attr"
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break

        if not _status:
            response = srl.data

            if len(srl_attr):
                response["attr"] = srl_attr
            
            response["status"], http = {
                "code"     : "S22",
                "message"  : "Instance updated",
                "warnings" : warns
            }, status.HTTP_201_CREATED
                                
        else:
            response = {"status" : _status} 
            
        rr = Response(response, status=http)

         # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/fireloc-i/{flocid}/',
            'service'  : 'manage-fireloc-result',
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
    
    def delete(self, request, flocid):
        """
        Delete result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            attr = FirelocAssessment.objects.get(pk=flocid)
        except FirelocAssessment.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Assessment Result doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            attr.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Assessment Result deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

         # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/fireloc-i/{flocid}/',
            'service'  : 'manage-fireloc-result',
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


class GetFlocAssess(APIView):
    """
    Fire Location Assessment results for unregisted
    users
    """

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - List Fire location assessment results
        for unregisted users
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        rq = request.query_params

        #startime = daytime - dt.timedelta(days=30)

        #objs = FirelocAssessment.objects.filter(startime__gte=startime)

        ctx = {
            "ctb" : None if "contribs" not in rq else \
                True if rq["contribs"] == 'true' else None,
            "epsg" : None if "epsg" not in rq else int(rq["epsg"]),
            "geom" : True if "geom" in rq and rq["geom"] == "true" else None,
            "extent" : True if "extent" in rq and rq["extent"] == "true" else None,
            "cctb" : None if "countcontribs" not in rq else \
                True if rq["countcontribs"] == 'true' else None
        }

        if "step" in rq:
            objs = FirelocAssessment.objects.filter(step=int(rq["step"]))
        
        else:
            objs = FirelocAssessment.objects.all()

        srl  = ReadFlocAssesSrl(objs, many=True, context=ctx)

        code, mess = "S20", "Data successfully returned"

        rr = Response({
            "status" : {"code" : code, "message" : mess},
            "data"   : srl.data
        }, status=status.HTTP_200_OK)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : 'floc/fireloc-uu/',
            'service'  : 'list-fireloc-results-uu',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : mess,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : None
        })

        if logsrl.is_valid(): logsrl.save()

        return rr


class FlocContributions(APIView):
    """
    Relate Contributions with Fire location assessment
    procedures
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def put(self, request, flocid):
        """
        Relate contributions with Fireloc Location
        Assessment procedures
        """

        from glass.pys import obj_to_lst

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, p = request.data, ["ctbs"]

        _status, http = check_rqst_param(p, list(d.keys()))

        if not _status:
            try:
                floc = FirelocAssessment.objects.get(pk=flocid)
            except FirelocAssessment.DoesNotExist:
                _status, http = {
                    "code"    : "I01",
                    "message" : "Assessment Result doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        # Check if contributions exist
        _ctbs = []
        if not _status:
            ctbs = obj_to_lst(d["ctbs"])

            for c in ctbs:
                try:
                    ctb = VolunteersContributions.objects.get(pk=int(c))
                    _ctbs.append(ctb)
                
                except VolunteersContributions.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Contribution doesn't exist."
                    }, status.HTTP_404_NOT_FOUND
                
                if _status: break
        
        # Update relations
        if not _status:
            for c in _ctbs:
                floc.ctbs.add(c)
            
            response, http = {"status" : {
                "code"    : "R21",
                "message" : "Relations were edited"
            }}, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-ctbs/{str(flocid)}/',
            'service'  : 'relate-floc-contrib',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user
        })

        if logsrl.is_valid(): logsrl.save()

        return rr


class FirelocLayerData(APIView):
    """
    Deal with data of the Fireloc Layers
    """

    permission_classes = [
        permissions.IsAdminUser,
        TokenHasReadWriteScope
    ]

    def post(self, request, lyr):
        """
        Receive Layer Raster data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None,

        dfolder = GEOMEDIA_FOLDERS.get('FLOC_RASTER', None)

        # Check if layer exists
        try:
            _lyr = MapFireAss.objects.get(slug=lyr)
        
        except MapFireAss.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Layer does not exist"
            }, status.HTTP_404_NOT_FOUND
        
        # Receive file and store it
        if not _status:
            rdata = request.FILES.get('flocraster')

            rst = os.path.join(dfolder, f"{lyr}.tif")

            with open(rst, 'wb+') as rf:
                for c in rdata.chunks():
                    rf.write(c)
            
            response, http = {"status" : {
                "code"    : "D01",
                "message" : "Fireloc Layer was edited",
            }}, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        r = Response(response, status=http)

        # Write logs
        logsrl = LogsFiredetectSrl(data={
            'url'      : f'floc/floc-raster/{str(lyr)}/',
            'service'  : 'fireloc-raster-data',
            'method'   : request.method,
            'http'     : r.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user
        })

        if logsrl.is_valid(): logsrl.save()

        return r

