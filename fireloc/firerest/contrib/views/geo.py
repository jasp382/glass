"""
Get contributions based on the geospatial relationship with other
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

from logs.srl import LogsContribSrl


class FindPlaces(APIView):
    """
    Association between Contribution and Place/Freguesia
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Retrieve contributions without place association
        with information about the nearest place and Freguesia
        """

        import numpy as np

        from glass.gp.prox.sql import st_near
        from glass.gp.ovl.sql  import points_in_polygons
        from firerest.settings import DATABASES

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        db = DATABASES["default"]["NAME"]

        # Run ST_Near - Get Place
        near_df = st_near(
            db, "contrib_volunteerscontributions", "geomc",
            "georef_places", "geom", near_col="distval",
            cols_in_tbl=["fid AS ctb_a"], until_dist="1000",
            intbl_pk="fid", cols_near_tbl=["fid AS lugid", "lugname"],
            whr_intbl="s.strips = 2", run_query=True
        )

        # Run ST_Contains - Get Freguesia
        freg_df = points_in_polygons(
            db, "contrib_volunteerscontributions", "geomc",
            "georef_freguesias", ["code AS fregid", "name AS fregname"], "geom",
            pnt_whr="pnt.strips = 2",
            pntattr=["fid AS ctb_b"]
        )

        # Merge results
        fres = near_df.merge(
            freg_df, how='outer', left_on='ctb_a', right_on='ctb_b'
        )

        fres['is_a'] = fres.ctb_a.isna()
        fres["fid"] = np.where(fres.is_a, fres.ctb_b, fres.ctb_a)

        fres["fid"] = fres.fid.astype(int)
        fres["distval"] = fres.distval.fillna(-1)
        fres["distval"] = fres.distval.round(0)
        fres["distval"] = fres.distval.astype(int)

        fres["lugid"] = fres.lugid.fillna(-1)
        fres["lugid"] = fres.lugid.astype(int)

        fres.drop(["ctb_a", "ctb_b", "is_a"], axis=1, inplace=True)

        data = [] if not fres.shape[0] else fres.to_dict(orient="records")

        code, msg = "S20", "Data successfully returned"

        response, http = {
            "status" : {"code": code, "message" : msg},
            "data"   : data
        }, status.HTTP_200_OK

        fresp = Response(response, http)

        # Write LOGS
        li = LogsContribSrl(data={
            'url'      : 'volu/ctb-places/',
            'service'  : 'contributions-places',
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

