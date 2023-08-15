"""
Relationship between objects and CAOP objects
"""


import datetime as dt
import pytz

# Rest Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.pys import obj_to_lst
from glass.sql.q import q_to_obj

from firerest.permcls  import IsFireloc
from firerest.settings import DATABASES

from georef.models import Freguesias, Concelhos
from events.models import RealFireEvents

from logs.srl import LogsEventSrl


class CaopRelFireEvents(APIView):
    """
    Retrieve Freguesias and Municipios related with
    Real Fire Events or update these relationships
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, caop):
        """
        Method GET - Retrive relationships
        ----
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        caop = 'freg' if caop != 'freg' and caop != 'mun' else caop
        tbl  =  'freguesias' if caop == 'freg' else 'concelhos'

        db = DATABASES["default"]["NAME"]

        q = (
            "SELECT foo.id, ARRAY_AGG(foo.code) AS caop "
            "FROM ("
                "SELECT mt.id, ("
                    "ST_Area(ST_intersection(mt.geom, caop.geom)) "
                    "* 100 / ST_Area(mt.geom)"
                ") AS tst, caop.* FROM ("
                    "SELECT tb.id, CASE "
                    "WHEN ST_IsValid(tb.geom) "
                    "THEN tb.geom "
                    "ELSE ST_MakeValid(tb.geom) "
                    "END AS geom FROM events_realfireevents AS tb "
                    f"LEFT JOIN events_realfireevents_{caop} AS jt "
                    f"ON tb.id = jt.realfireevents_id "
                    f"WHERE jt.{tbl}_id IS NULL"
                ") AS mt "
                f"INNER JOIN georef_{tbl} AS caop "
                "ON ST_Intersects(mt.geom, caop.geom) "
            ") AS foo "
            "WHERE foo.tst > 30 "
            "GROUP BY foo.id "
            "ORDER BY foo.id"
        )

        data = q_to_obj(db, (
            "SELECT ARRAY_AGG(row_to_json(restbl)) AS data FROM ("
            f"{q}) AS restbl"
        ), dbset="default")

        val = [] if not data["data"][0] else data["data"][0]

        code, msg = "S20", "Data successfully returned"

        response  = {
            "status" : {"code" : code, "message" : msg},
            "data"   : val
        }

        rr = Response(response, status=status.HTTP_200_OK)

        # Write Logs
        ls = LogsEventSrl(data={
            'url'      : 'events/firecaop/',
            'service'  : 'fire-events-caop',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : code,
            'message'  : msg,
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def put(self, request, caop):
        """
        Method PUT - Write relationships
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        caop = 'freg' if caop != 'freg' and caop != 'mun' else caop
        mdl  = Freguesias if caop == 'freg' else Concelhos

        # Check if we have data
        levents = list(d.keys())

        if not len(levents):
            _status, http = {
                "code"    : "E01",
                "message" : "No events to process"
            }, status.HTTP_400_BAD_REQUEST

        # Check if all events exists
        events = {}
        if not _status:
            for k in d:
                try:
                    events[k] = RealFireEvents.objects.get(pk=int(k))
                
                except RealFireEvents.DoesNotExist:
                    _status, http = {
                        "code"    : "I01",
                        "message" : "Event doesn't exist."
                    }, status.HTTP_400_BAD_REQUEST

                    break
        
        # Check if all caop objects exist's
        if not _status:
            for k in d:
                d[k] = obj_to_lst(d[k])

                if not d[k]:
                    _status, http = {
                        "code"    : "Z01",
                        "message" : f"Event {k} doesn't have CAOP objects"
                    }, status.HTTP_400_BAD_REQUEST

                    break

                for i in range(len(d[k])):
                    try:
                        d[k][i] = mdl.objects.get(code=d[k][i])
                    
                    except mdl.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "CAOP Object doesn't exist."
                        }   , status.HTTP_400_BAD_REQUEST

                        break
        
        # Relate objects
        if not _status:
            for e in d:
                for o in d[e]:
                    if caop == 'freg':
                        events[e].freg.add(o)
                    else:
                        events[e].mun.add(o)
            
            response, http = {"status" : {
                "code"    : "R21",
                "message" : "Relations were created"
            }}, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write Logs
        ls = LogsEventSrl(data={
            'url'      : 'events/firecaop/',
            'service'  : 'fire-events-caop',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr
    
    def delete(self, request, caop):
        """
        Method Delete  - Delete all relationships
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        caop = 'freg' if caop != 'freg' and caop != 'mun' else caop

        # Get Fire Events
        events = RealFireEvents.objects.all()

        for e in events:
            if caop == 'freg':
                relo = e.freg.all()

                for o in relo:
                    e.freg.remove(o)
            
            else:
                relo = e.mun.all()

                for o in relo:
                    e.mun.remove(o)
        
        response, http = {"status" : {
            "code"    : "R22",
            "message" : "Relations were deleted"
        }}, status.HTTP_200_OK

        rr = Response(response, status=http)

        # Write Logs
        ls = LogsEventSrl(data={
            'url'      : 'events/firecaop/',
            'service'  : 'fire-events-caop',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if ls.is_valid(): ls.save()

        return rr


class FindPlacesFreg(APIView):
    """
    Association between Fire Events Locations and 
    Places/Freguesia
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Retrieve fire locations without place association and
        relate with places and freguesias
        """

        from glass.gp.prox.sql   import near_cntr_inside_poly
        from glass.tbl.joins.sql import join_by_intersect
        from firerest.settings   import DATABASES

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        db = DATABASES["default"]["NAME"]

        # Get places
        pdf = near_cntr_inside_poly(
            db, "events_realfireevents", "georef_places",
            'id', 'geom', 'geom',
            poly_cols={"fireid_a" : "id"},
            pnt_cols={"placeid" : "fid"},
            whrpoly="poly.step = 0"
        )

        # Get freguesias
        fdf = join_by_intersect(
            db, "events_realfireevents", "georef_freguesias",
            'id', 'geom','geom',
            cols_a={"fireid_b" : "id"},
            cols_b={"fregid" : "code"},
            whr_a="ta.step = 0",
            forcegeoma=True
        )

        # Merge results
        fres = pdf.merge(
            fdf, how='outer', left_on='fireid_a',
            right_on='fireid_b'
        )

        fres.rename(columns={'fireid_b' : 'id'}, inplace=True)
        fres.drop(['fireid_a'], axis=1, inplace=True)
        fres['placeid'] = fres.placeid.fillna(-1)
        fres['placeid'] = fres.placeid.astype(int)

        data = [] if not fres.shape[0] else fres.to_dict(orient="records")
        print(data)

        code, msg = "S20", "Data successfully returned"

        response, http = {
            "status" : {"code": code, "message" : msg},
            "data"   : data
        }, status.HTTP_200_OK

        fresp = Response(response, http)

        # Write LOGS
        li = LogsEventSrl(data={
            'url'      : 'events/fires-places/',
            'service'  : 'fire-find-places',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp

