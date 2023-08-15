"""
Contributions intersection
"""

import datetime as dt
import pytz
import itertools


# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from glass.sql.q     import q_to_obj
from firerest.settings import DATABASES

from contrib.models import VolunteersContributions

from firerest.permcls import IsFireloc

from logs.srl import LogsContribSrl



class CtbIntersectCtb(APIView):
    """
    Return Contributions intersecting with each
    Contribution
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes     = [JSONParser]


    def get(self, request, step):
        """
        Run Intersection and return the result
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        db = DATABASES["default"]["NAME"]

        # Get query params
        d = request.query_params.copy()

        # Check if starttime and endtime values are valid
        for st in ["starttime", "endtime"]:
            if st not in d: continue

            try:
                tt = dt.datetime.strptime(d[st], '%Y-%m-%d-%H-%M-%S')
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" :  f"{st} has not the right format"
                }, status.HTTP_400_BAD_REQUEST
            
            if _status: break
        
        # Get data - Launch query to the PSQL Server
        if not _status:
            stime = "" if "starttime" not in d else (
                f"AND mt.datehour >= TO_TIMESTAMP('"
                f"{d['starttime']}', 'YYYY-MM-DD-HH24-MI-SS') "
            )

            etime = "" if "endtime" not in d else (
                f"AND mt.datehour <= TO_TIMESTAMP('"
                f"{d['endtime']}', 'YYYY-MM-DD-HH24-MI-SS') "
            )
            
            q = (
                "SELECT ctb_a.fid AS ctb_a, "
                "ARRAY_AGG(ctb_b.fid ORDER BY ctb_b.fid) AS ctb_b "
                "FROM contrib_volunteerscontributions AS ctb_a, "
                "contrib_volunteerscontributions AS ctb_b "
                "WHERE ctb_a.fid < ctb_b.fid AND "
                f"ctb_a.strips = {str(step)} AND ctb_b.strips = {str(step)} AND "
                "ST_Intersects(ctb_a.stripgeom, ctb_b.stripgeom) "
                f"{stime}{etime}"
                "GROUP BY ctb_a.fid "
                "ORDER BY ctb_a.fid"
            )

            data = q_to_obj(db, (
                "SELECT ARRAY_AGG(row_to_json(foo)) AS data FROM ("
                f"{q}) AS foo"
            ), dbset="default")

            val = [] if not data["data"][0] else data["data"][0]

            code, msg = "S20", "Data successfully returned"

            response, http = {
                "status" : {"code": code, "message" : msg},
                "data"   : val
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        fresp = Response(response, http)

        # Write LOGS
        li = LogsContribSrl(data={
            'url'      : 'volu/ctb-i-ctb/',
            'service'  : 'contributions-intersection',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp


class CtbGroupsValidate(APIView):
    """
    Validate Contributions Groups

    See if intersection of all contributions
    returns a polygon. If not, create subgroups
    with lesser contributions.
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes     = [JSONParser]

    def get_intersection_area_query(self, ctbs, refid):
        ctbs_q = [(
            f"SELECT {refid} AS jid, ctb.fid AS fid_{str(i)}, "
            f"ctb.stripgeom AS sgeom_{str(i)} "
            "FROM contrib_volunteerscontributions AS ctb "
            f"WHERE ctb.fid = {ctbs[i]}"
        ) for i in range(len(ctbs))]

        ljq = [(
            f"LEFT JOIN ({ctbs_q[i]}) AS ctb_{str(i)} "
            f"ON ctb.jid = ctb_{str(i)}.jid"
        ) for i in range(1, len(ctbs_q))]

        intq = ctbs_q.copy()
        intq[1] = "ST_Intersection(sgeom_0, sgeom_1)"
        for i in range(2, len(intq)):
            intq[i] = f"ST_Intersection({intq[i-1]}, sgeom_{str(i)})"
        
        q = (
            f"SELECT ctb.jid, ST_Area({intq[-1]}) AS intarea "
            f"FROM ({ctbs_q[0]}) AS ctb {' '.join(ljq)}"
        )
    
        return q

    def get(self, request):
        """
        Do the job
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        db = DATABASES["default"]["NAME"]

        # Get query params
        d = request.query_params.copy()

        if "ctbs" not in d:
            _status, http = {
                "code"    : "E01",
                "message" : "Query parameters are not valid; ctbs is not in request"
            }, status.HTTP_400_BAD_REQUEST
        
        # See if contributions exist
        if not _status:
            ctbs_id = d["ctbs"].split(',')

            for c in range(len(ctbs_id)):
                try:
                    ctb = VolunteersContributions.objects.get(fid=int(ctbs_id[c]))

                    ctbs_id[c] = ctb.fid

                except VolunteersContributions.DoesNotExist:
                    _status, http =  {
                        "code"    : "I01",
                        "message" : "Contribution doesn't exist"
                    }, status.HTTP_404_NOT_FOUND

                    break
        
        # Validate and create new groups if necessary
        if not _status:
            mq = self.get_intersection_area_query(ctbs_id, 1)

            res = q_to_obj(db, mq)

            res = res[res.intarea >= 10000]

            if not res.shape[0]:
                valid_groups = None
                ngroups = []
            
            else:
                valid_groups = True
                ngroups = [ctbs_id]

            level = 1

            while not valid_groups:
                ngrp = len(ctbs_id) - level
                if ngrp < 2:
                    valid_groups = True
    
                subgroups = list(itertools.combinations(ctbs_id, ngrp))

                subqueries = [self.get_intersection_area_query(
                    list(subgroups[g]), g + 1
                ) for g in range(len(subgroups))]

                fq = " UNION ALL ".join(subqueries)

                res_v = q_to_obj("fireloc_db", fq)
    
                res_v = res_v[res_v.intarea >= 10000]
    
                if not res_v.shape[0]:
                    level += 1
                    continue
    
                else:
                    for i in res_v.jid.tolist():
                        ngroups.append(list(subgroups[i - 1]))
        
                    valid_groups = True
            
            code, msg = "S20", "Data successfully returned"
            
            response, http = {
                "status" : {"code": code, "message" : msg},
                "data"   : ngroups
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        fresp = Response(response, http)

        # Write LOGS
        li = LogsContribSrl(data={
            'url'      : 'volu/ctb-val/',
            'service'  : 'ctb-intersection-validation',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp

