"""
Proximity fire locations analysis
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

from firerest.permcls import IsFireloc

from logs.srl import LogsFiredetectSrl


class OldLocsNearNew(APIView):
    """
    Identify near Fire Locations

    Fire locations centroids with
    distances under 5000 meters of each other 
    are considered near.
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]

    parser_classes     = [JSONParser]

    def get(self, request):
        """
        Retrieve near Fire Locations
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        db = DATABASES["default"]["NAME"]
        qp = request.query_params

        cstep = "6" if "cstep" not in qp else qp["cstep"]
        fstep = "7" if "fstep" not in qp else qp["fstep"]

        q = (
            "SELECT array[ida] || array_remove(ARRAY_AGG(idb), NULL) AS flocs "
            "FROM ("
                "SELECT ida, CASE "
                    "WHEN foo.cdist <= 5000 THEN foo.idb "
                    "ELSE NULL "
                "END AS idb, cdist FROM ("
                    "SELECT floc_a.id AS ida, floc_b.id AS idb, "
		            "ST_Distance("
                        "ST_Centroid(floc_a.geom), "
                        "ST_Centroid(floc_b.geom)"
                    ") AS cdist "
		            "FROM detect_firelocassessment AS floc_a, "
		            "detect_firelocassessment AS floc_b "
		            f"WHERE floc_a.step={cstep} AND floc_b.step={fstep}"
                ") AS foo"
            ") AS cue GROUP BY ida"
        )

        data = q_to_obj(db, q, dbset="default")

        val = data.flocs.tolist()

        code, msg = "S20", "Data successfully returned"

        response, http = {
            "status" : {"code": code, "message" : msg},
            "data"   : val
        }, status.HTTP_200_OK

        fresp = Response(response, http)

        # Write logs
        li = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-near-floc/',
            'service'  : 'fireloc-near-fireloc',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(qp[k])}" for k in qp]),
            'cuser'    : request.user.pk
        })

        if li.is_valid(): li.save()

        return fresp

