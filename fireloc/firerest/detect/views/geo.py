"""
Get fire locations based on the geospatial relationship with other
geospatial objects in the database
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

from firerest.permcls import IsFireloc

from logs.srl import LogsFiredetectSrl


class FindPlacesFreg(APIView):
    """
    Association between Fireloc Locations and 
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
            db, "detect_firelocassessment", "georef_places",
            'id', 'geom', 'geom',
            poly_cols={"fireid_a" : "id"},
            pnt_cols={"placeid" : "fid"},
            whrpoly="poly.step = 6"
        )

        # Get freguesias
        fdf = join_by_intersect(
            db, "detect_firelocassessment", "georef_freguesias",
            'id', 'geom','geom',
            cols_a={"fireid_b" : "id"},
            cols_b={"fregid" : "code"},
            whr_a="ta.step = 6"
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

        code, msg = "S20", "Data successfully returned"

        response, http = {
            "status" : {"code": code, "message" : msg},
            "data"   : data
        }, status.HTTP_200_OK

        fresp = Response(response, http)

        # Write LOGS
        li = LogsFiredetectSrl(data={
            'url'      : 'floc/floc-places/',
            'service'  : 'floc-find-places',
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

