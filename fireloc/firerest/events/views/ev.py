"""
Real events management
"""


import datetime as dt
import pytz
from osgeo import ogr

# Rest Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.gobj import wkt_sanitize, polygon_to_multipolygon
from glass.sql.q import q_to_obj

from firerest.settings import DATABASES
from firerest.permcls  import IsFireloc
from firerest.utils    import check_rqst_param
from authapi.utils     import id_usertype

from events.models import RealFireEvents
from georef.models import Places, Freguesias
from events.srl import RealFireEventsSrl, ReadFireSrl

from logs.srl import LogsEventSrl


# ########################################### #
# ########## Get Fire Events Logic ########## #
# ########################################### #


def get_fire_events(qp):
    """
    Get Fire Events and return them to the respective
    endpoint
    """

    _status, http = None, None

    db = DATABASES["default"]["NAME"]

    # Check if starttime and endtime values are valid
    for st in ["starttime", "endtime"]:
        if st not in qp: continue

        try:
            tt = dt.datetime.strptime(qp[st], '%Y-%m-%d-%H-%M-%S')
        except:
            _status, http = {
                "code"    : "E07",
                "message" :  f"{st} has not the right format"
            }, status.HTTP_400_BAD_REQUEST
            
        if _status: break
    
    # Check if geometry is valid
    if not _status and "fgeom" in qp:
        a = ogr.CreateGeometryFromWkt(qp["fgeom"])

        if not a.IsValid():
            _status, http = {
                "code"    : "G01",
                "message" :  f"Geometry object is not valid"
            }, status.HTTP_400_BAD_REQUEST
    
    # Get data - Launch query to the PSQL Server
    if not _status:
        epsg = True if "epsg" in qp else str(qp['epsg'])
        geom = True if "geom" in qp and qp["geom"] == "true" else None
        fepsg = qp["fepsg"] if "fepsg" in qp and \
            str(qp["fepsg"]) != '3763' else None


        geomcol = "NULL AS geom" if not geom else "ST_AsText(foo1.geom) AS geom" \
            if geom and not epsg else \
                f"ST_AsText(ST_Transform(foo1.geom, {qp['epsg']})) AS geom" \
                    if geom and epsg else "NULL AS geom"
            
        barea = "NULL AS burnedarea" if "barea" in qp and qp["barea"] == "false" else \
            "ROUND(CAST((ST_Area(foo1.geom) / 10000) AS decimal), 2) AS burnedarea" \
                if not epsg else \
                    f"ROUND(CAST((ST_Area(ST_Transform(foo1.geom, {qp['epsg']})) / 10000) AS decimal), 2) AS burnedarea"
        
        # Where
        whr_str = {
            "starttime" : "" if "starttime" not in qp else (
                f"tb.start >= TO_TIMESTAMP('"
                f"{qp['starttime']}', 'YYYY-MM-DD-HH24-MI-SS')"
            ),
            "endpoint" : "" if "endtime" not in qp else (
                f"tb.end <= TO_TIMESTAMP('"
                f"{qp['endtime']}', 'YYYY-MM-DD-HH24-MI-SS')"
            ),
            "fgeom" : "" if "fgeom" not in qp else (
                f"ST_intersects({'ST_Transform(' if fepsg else ''}"
                f"ST_GeomFromText('{qp['fgeom']}', "
                f"{str(qp['fepsg']) if fepsg else '3763'})"
                f"{', 3763)' if fepsg else ''}, tb.geom"
            ")")
        }

        whrlst = [whr_str[k] for k in whr_str if whr_str[k] != '']

        whr = "" if not len(whrlst) else \
            f" WHERE {' AND '.join(whrlst)} "
        
        lmt = "" if "limit" not in qp else f" LIMIT {str(qp['limit'])}"

        place_case = (
            "CASE "
                "WHEN foo1.nearplace IS NULL THEN NULL "
                "ELSE json_build_object("
                    "'fid', gp.fid, 'lugid', gp.lugid, 'lugname', gp.lugname, "
                    "'altname', gp.altname, "
                    "'geom', ST_AsText(gp.geom), "
                    "'fregid', gp.freg, 'source', gp.source"
                ")"
            "END"
        )

        freg_case = (
            "CASE "
                "WHEN foo1.fregid IS NULL THEN NULL "
                "ELSE json_build_object("
                    "'fid', gfreg.fid, 'code', gfreg.code, "
                    "'name', gfreg.name, 'munid', gfreg.munid "
                ")"
            "END"
        )

        q = (
            "SELECT foo1.id, foo1.tipo, foo1.causa, foo1.name, "
            f"foo1.codsgif, foo1.codncco, {geomcol}, {barea}, "
            "to_char(foo1.start, 'YYYY-MM-DD HH24:MI:SS') AS start, "
            "to_char(foo1.end, 'YYYY-MM-DD HH24:MI:SS') AS end, "
            "foo1.freg, foo2.mun AS mun, lyr.firelyr AS firelyr, "
            f"{place_case} AS nearplace, {freg_case} AS fregid "
            "FROM ("
                "SELECT tb.*, "
                "CASE "
                    "WHEN ft.realfireevents_id IS NULL THEN NULL "
                    "ELSE ARRAY_AGG(json_build_object("
                        "'fid', ft.fid, 'code', ft.code, "
		                "'name', ft.name, 'munid', ft.munid"
                    "))"
                "END AS freg "
                "FROM events_realfireevents AS tb "
                "LEFT JOIN ("
                    "SELECT freg.*, frel.realfireevents_id "
                    "FROM georef_freguesias AS freg "
                    "LEFT JOIN events_realfireevents_freg AS frel "
                    "ON freg.fid = frel.freguesias_id"
                ") AS ft "
                "ON tb.id = ft.realfireevents_id "
                f"{whr}"
                "GROUP BY tb.id, tb.codsgif, tb.codncco, tb.tipo, tb.causa, "
                "tb.name, tb.start, tb.end, tb.geom, ft.realfireevents_id "
                "ORDER BY tb.id"
                f"{lmt}"
            ") AS foo1 "
            "INNER JOIN ("
                "SELECT tb.id, "
	            "CASE "
		            "WHEN mt.realfireevents_id IS NULL THEN NULL "
	 	            "ELSE ARRAY_AGG(json_build_object("
			            "'fid', mt.fid, 'code', mt.code, "
		 	            "'name', mt.name, 'nutiii', mt.nutiii"
		            "))"
	            "END AS mun "
	            "FROM events_realfireevents AS tb "
	            "LEFT JOIN ( "
		            "SELECT mun.*, mrel.realfireevents_id "
		            "FROM georef_concelhos AS mun "
		            "LEFT JOIN events_realfireevents_mun AS mrel "
		            "ON mun.fid = mrel.concelhos_id"
	            ") AS mt "
	            "ON tb.id = mt.realfireevents_id "
                f"{whr}"
	            "GROUP BY tb.id, mt.realfireevents_id "
                "ORDER BY tb.id"
                f"{lmt}"
            ") AS foo2 "
            "ON foo1.id = foo2.id "
            "INNER JOIN ("
                "SELECT tb.id AS fireid, "
                "CASE "
                    "WHEN lt.fireid IS NULL THEN NULL ELSE "
                    "ARRAY_AGG(json_build_object("
                        "'id', lt.id, 'slug', lt.slug, "
                        "'design', lt.design, 'work', work, "
                        "'store', lt.store, 'glyr', glyr, "
                        "'style', style, 'fireid', fireid"
                    ")) "
                "END AS firelyr "
                "FROM events_realfireevents AS tb "
                "LEFT JOIN geovis_eventslayers AS lt "
                "ON tb.id = lt.fireid "
                f"{whr}"
                "GROUP BY tb.id, lt.fireid "
                "ORDER BY tb.id"
                f"{lmt}"
            ") AS lyr "
            "ON foo1.id = lyr.fireid "
            "LEFT JOIN georef_places AS gp "
            "ON foo1.nearplace = gp.fid "
            "LEFT JOIN georef_freguesias AS gfreg "
            "ON foo1.fregid = gfreg.fid "
            "ORDER BY foo1.id"
        )

        data = q_to_obj(db, (
            "SELECT ARRAY_AGG(row_to_json(ev)) AS data FROM ("
            f"{q}) AS ev"
        ), dbset="default")

        val = [] if not data["data"][0] else data["data"][0]

        code, msg = "S20", "Data successfully returned"

        response, http  = {
            "status" : {"code" : code, "message" : msg},
            "data"   : val
        }, status.HTTP_200_OK
    
    else:
        response = {"status" : _status}

    return response, http


# ########################################### #
# ########################################### #


class ManRFireEvents(APIView):
    """
    Manage Real Fire Events
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all fire events
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get Response
        d = request.query_params.copy()

        response, http = get_fire_events(d)

        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/real-fires/',
            'service'  : 'manage-rfire-events',
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
    

    def post(self, request):
        """
        Method POST - Add new event
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        # Get user and user type
        cuser, ustype = request.user, id_usertype(cuser)

        pp, op = [
            "start", "geom", "epsg", "end", "timezone"
        ], [
            "codsgif", "codncco", "tipo", "causa", "name"
        ]

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        # Check Request Parameters
        if not _status:
            _status, http = check_rqst_param(pp, list(d.keys()))
 
        # Check timezone
        if not _status:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Check if starttime and endtime values are valid
            for time in ["end", "start"]:
                try:
                    tt = dt.datetime.strptime(d[time], '%Y-%m-%d %H:%M:%S')
                    _tz = pytz.timezone(d["timezone"])

                    d[time] = _tz.localize(tt)
                
                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"{time} has not the right format"
                    }, status.HTTP_400_BAD_REQUEST
                
                if _status: break
        
        # Handling Polygon
        if not _status:
            d["geom"] = polygon_to_multipolygon(d["geom"])

            if not d["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : "Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            d["geom"] = wkt_sanitize(
                d["geom"], rgeos=True,
                epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                reprj=None if d["epsg"] == 3763 else 3763
            )

            if not d["geom"]:
                _status, http = {
                    "code"    : "G01",
                    "message" : f"geom key | Geometry is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        #check if freguesia exists
        if not _status and "fregid" in d:
            try:
                freg = Freguesias.objects.get(code=d["fregid"])
                d["fregid"] = freg.id
                
            except Freguesias.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Freguesia {d['fregid']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND
        
        else:
            d["fregid"] = None
        
        # Check if place exist
        if not _status and "nearplace" in d:
            try:
                pid = Places.objects.get(pk=d["nearplace"])
                
            except Places.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : f"Place {d['nearplace']} doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        if not _status:
            for p in op:
                if p not in d:
                    d[p] = None
            
            d["step"] = 0
            
            srl = RealFireEventsSrl(data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Real Fire Event added."
                }, status.HTTP_201_CREATED
                
            else:
                response, http = {"status":{
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status}
    
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/real-fires/',
            'service'  : 'manage-rfire-events',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request):
        """
        Method DELETE - Delete all events
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
       
        # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            RealFireEvents.objects.all().delete()
            
            response, http = {"status" : {
                "code"    : "S24",
                "message" : "Real Fire Events deleted"
            }}, status.HTTP_200_OK

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

         # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/real-fires/',
            'service'  : 'manage-rfire-events',
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


class ManRFireEvent(APIView):
    """
    Manage Real Fire Event
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, fid):
        """
        Method GET - Retrieve data of a fire event
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.query_params

        ctx = {
            "epsg" : None if "epsg" not in d else int(d["epsg"]),
            "geom" : True if "geom" in d and d["geom"] == "true" else None,
            "barea" : None if "barea" in d and d["barea"] == "false" else None 
        }
        
        try:
            fe = RealFireEvents.objects.get(pk=fid)
        except RealFireEvents.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Real Fire Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            srl = ReadFireSrl(fe, context=ctx)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
            
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/real-fire/{str(fid)}/',
            'service'  : 'manage-rfire-event',
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
    

    def put(self, request, fid):
        """
        Method PUT - update existing event
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = [
            "codsgif", "codncco", "tipo", "causa",
            "start", "end", "geom", "name",
            "fregid", "nearplace", "step"
        ]

        try:
            fe = RealFireEvents.objects.get(pk=fid)
            srl = RealFireEventsSrl(fe)
            srldata = srl.data
        
        except RealFireEvents.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Real Fire Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        warns = []
        if not _status:
            for p in rp:
                if p == 'geom' and 'epsg' not in d:
                    d[p] = srldata[p]

                    warns.append('geom not updated - epsg code is missing')
                    continue
                
                elif p == 'geom' and 'epsg' in d:
                    d[p] = wkt_sanitize(
                        d[p],
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj=None if d["epsg"] == 3763 else 3763,
                        rgeos=True
                    )

                    if not d[p]:
                        d[p] = srldata[p]

                        warns.append('geom not updated - geom is invalid')
                    
                    continue

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

                if p not in d:
                    d[p] = srldata[p]
                      
            srl = RealFireEventsSrl(fe, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Real Fire Event was updated.",
                    "warnings" : warns
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
        logsrl = LogsEventSrl(data={
            'url'      : f'events/real-fire/{str(fid)}/',
            'service'  : 'manage-rfire-event',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d if k != 'geom']),
            'cuser'    : request.user.pk
        })

        if logsrl.is_valid(): logsrl.save()

        return rr
    
    def delete(self, request, fid):
        """
        Method DELETE - Delete an event
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            fe = RealFireEvents.objects.get(pk=fid)
        except RealFireEvents.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Real Fire Event doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            fe.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Real Fire Event deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : f'events/real-fire/{str(fid)}/',
            'service'  : 'manage-rfire-event',
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


class GetRFireEvents(APIView):
    """
    Get Real Fire Events
    """

    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all fire events
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get Response
        d = request.query_params.copy()

        response, http = get_fire_events(d)

        rr = Response(response, status=http)
        
        # Write logs
        logsrl = LogsEventSrl(data={
            'url'      : 'events/rfires-uu/',
            'service'  : 'list-rfire-uu',
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

