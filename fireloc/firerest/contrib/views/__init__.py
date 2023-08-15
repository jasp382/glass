"""
Volunteer Contributions Views
"""

import datetime as dt
import pytz
import os

from osgeo import ogr

from glass.pys.oss import lst_ff, del_file

# REST Framework Dependencies
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import JSONParser

from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope

from django.contrib.auth.models import User
from contrib.models import VolunteersContributions, VolunteersPositions
from contrib.models import VolunteersPositionsBackFront
from georef.models import Freguesias, Places
from contrib.srl import ContribSrl, ReadContrib
from contrib.srl import ContribPositionsSrl, ContribPosistionsBackFrontSrl

from firerest.settings import GEOMEDIA_FOLDERS

from firerest.utils import check_rqst_param
from contrib.utils import get_photo

from authapi.utils import id_usertype

from logs.srl import LogsContribSrl

from glass.gobj import wkt_sanitize, get_centroid
from glass.prj.obj import prj_ogrgeom


class ManContributions(APIView):
    """
    List and Create user Contributions
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]
    parser_classes     = [JSONParser]

    def get(self, request):
        """
        List Volunteers Contributions

        Parameters:
        geom - return geom field
        usergeom - return usergeom field
        geombf = return geombf field
        epsg - EPSG to apply to all geometries

        i_date = inital Date dd/mm/yyyy
        f_date = final Date dd/mm/yyyy 
        poly = bounding box  GEOSGeometry(poly,srid)
        poly = POLYGON((1 1, 1 2 , 2 1, 2 2, 1 1))
        srid = epsg poly.transfrom(srid)
        """

        from glass.sql.q     import q_to_obj
        from glass.prop.sql  import cols_name
        from firerest.settings import DATABASES

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        db = DATABASES["default"]["NAME"]

        # Get query params
        d = request.query_params.copy()
        
        # Get current user
        cuser  = request.user
        ustype = id_usertype(cuser)

        # Check if user is Superuser or Fireloc User
        # Check user privileges
        # If Superuser or Fireloc User return all contributions
        # If justauser return only the user contributions
        if ustype != 'superuser' and ustype != 'fireloc' and ustype != 'riskmanager':
            d["userid"] = str(cuser.id)
        
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
            orient = 'date' if 'orient' in d and d['orient'] \
                == 'date' else 'records'
            
            geomc_type = d["geomctype"] if "geomctype" in d else 'wkt'
            geomc_type = 'wkt' if geomc_type != 'wkt' and geomc_type \
                != 'coords' else geomc_type

            epsg = None if "epsg" not in d else str(d["epsg"])
            fepsg = d["fepsg"] if "fepsg" in d and \
                str(d["fepsg"]) != '3763' else None
            geom = True if "geom" in d and d["geom"] == "true" else None
            
            usergeom = True if "usergeom" in d and d["usergeom"] == "true" \
                else None
            
            geombf = True if "geombf" in d and d["geombf"] == "true" \
                else None
            
            _geomc = True if "geomc" in d and d["geomc"] == "true" \
                else None
            
            _geombfc = True if "geombfc" in d and d["geombfc"] == "true" \
                else None
            
            geomcisna = True if "geomcisna" in d and d["geomcisna"] == "true" \
                else False if "geomcisna" in d and d["geomcisna"] == "false" \
                    else None
            
            placeisna = True if "placeisna" in d and d["placeisna"] == "true" \
                else False if "placeisna" in d and d["placeisna"] == "false" \
                    else None
            
            showlayers = True if "layers" in d and d["layers"] == "true" \
                else None if "layers" in d and d["layers"] == "false" \
                    else None
            
            bounds = True if "bounds" in d and d["bounds"] == "true" \
                else None if "bounds" in d and d["bounds"] == "false" \
                    else None

            q_geom = (
                "LEFT JOIN ("
                    "SELECT cid, ARRAY_AGG(json_build_object("
                        "'pid', pid, 'azimute', azimute, 'geom', {gcol}"
                    ") ORDER BY cid, pid) AS gdata "
                    "FROM {tbl} "
                    "GROUP BY cid"
                ") AS {alias} "
                "ON mt.fid = {alias}.cid "
            )

            geomcol = "" if not geom else "ST_AsText(geom)" \
                if geom and not epsg else \
                    f"ST_AsText(ST_Transform(geom, {epsg}))" \
                        if geom and epsg else ""

            geomstr = "" if not geom else q_geom.format(
                gcol=geomcol, tbl="contrib_volunteerspositions",
                alias="cp"
            )
            
            usgeom = "" if not usergeom else ", ST_AsText(mt.usergeom) AS usergeom" \
                if usergeom and not epsg else \
                    f", ST_AsText(ST_Transform(mt.usergeom, {epsg})) AS usergeom" \
                        if usergeom and epsg else None
            
            if _geomc and not epsg and geomc_type == 'wkt':
                geomc = ", ST_AsText(mt.geomc) AS geomc"
            
            elif _geomc and epsg and geomc_type == 'wkt':
                geomc = f", ST_AsText(ST_Transform(mt.geomc, {epsg})) AS geomc"
            
            elif _geomc and not epsg and geomc_type == 'coords':
                geomc = (f", json_build_object("
                    "'x_coord', ST_X(mt.geomc), "
                    "'y_coord', ST_Y(mt.geomc)"
                ") AS geomc")
            
            elif _geomc and epsg and geomc_type == 'coords':
                geomc = (f", json_build_object("
                    f"'x_coord', ST_X(ST_Transform(mt.geomc, {epsg})), "
                    f"'y_coord', ST_Y(ST_Transform(mt.geomc, {epsg}))"
                ") AS geomc")
            
            else:
                geomc = ""
            
            geombfc = "" if not _geombfc else ", ST_AsText(mt.geombfc) AS geombfc" \
                if _geombfc and not epsg else \
                    f", ST_AsText(ST_Transform(mt.geombfc, {epsg})) AS geombfc" \
                        if _geombfc and epsg else None
            
            bfgeom = "" if not geombf else q_geom.format(
                gcol=geomcol, alias="cbf",
                tbl="contrib_volunteerspositionsbackfront"
            )

            selgeom = "" if not geom else ", cp.gdata AS geom "
            selgeombf = "" if not geombf else ", cbf.gdata AS geombf "

            needemail=None

            whr_str = {
                "userid" : "",
                "starttime" : "" if "starttime" not in d else (
                    f"mt.datehour >= TO_TIMESTAMP('"
                    f"{d['starttime']}', 'YYYY-MM-DD-HH24-MI-SS')"
                ),
                "endtime" : "" if "endtime" not in d else (
                    f"mt.datehour <= TO_TIMESTAMP('"
                    f"{d['endtime']}', 'YYYY-MM-DD-HH24-MI-SS')"
                ),
                "fgeom" : "" if "fgeom" not in d else (
                    f"ST_Contains({'ST_Transform(' if fepsg else ''}"
                        f"ST_GeomFromText('{d['fgeom']}', "
                        f"{str(d['fepsg']) if fepsg else '3763'})"
                        f"{', 3763)' if fepsg else ''}, mt.usergeom"
                    ")"
                ),
                "geomc" : f"geomc IS NULL" if geomcisna == True else \
                    f"geomc IS NOT NULL" if geomcisna == False else "",
                "place" : f"place IS NULL" if placeisna == True else \
                    f"place IS NOT NULL" if placeisna == False else "",
                "strips" : f"strips = {d['strips']}" if \
                    "strips" in d else "",
                "photostatus" : f"photostatus = {d['photostatus']}" if \
                    "photostatus" in d else ""
            }

            if "userid" in d:
                if d["userid"] == "true":
                    whr_str["userid"] = f"cuser={str(cuser.id)}"
                
                else:
                    try:
                        usid = int(d["userid"])
                        whr_str["userid"] = f"cuser={str(usid)}"
                    
                    except ValueError as verr:
                        # Assuming we have an e-mail
                        whr_str["userid"] = f"ut.email='{d['userid']}'"
                        needemail = True
            
            whrlst = [whr_str[k] for k in whr_str if whr_str[k] != '']

            whr = "" if not len(whrlst) else \
                f" WHERE {' AND '.join(whrlst)}"

            lmt = "" if "limit" not in d else f" LIMIT {str(d['limit'])}"

            usnamecol = "" if "rusername" not in d else "ut.email, "
            usjoin = "" if "rusername" not in d and not needemail else (
                "LEFT JOIN auth_user AS ut "
                "ON mt.cuser = ut.id "
            )

            place_case = (
                "CASE "
                    "WHEN mt.place IS NULL THEN NULL "
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
                    "WHEN mt.fregid IS NULL THEN NULL "
                    "ELSE json_build_object("
                        "'fid', gfreg.fid, 'code', gfreg.code, "
                        "'name', gfreg.name, 'munid', gfreg.munid "
                    ")"
                "END"
            )

            if showlayers:
                ctb_cols = cols_name(db, "contrib_volunteerscontributions")
                cols_str = ", ".join([f"ctb.{c}" for c in ctb_cols])
                ctb_tbl = (
                    f"(SELECT {cols_str}, ARRAY_AGG(json_build_object("
                        "'id', lyr.id, 'slug', lyr.slug, "
                        "'desig', lyr.desig, 'work', lyr.work, "
	                    "'store', lyr.store, 'layer', lyr.layer,"
	                    "'style', lyr.style, 'wms', lyr.wms, "
	                    "'ctb', lyr.ctb"
                    ")) AS layers "
                    "FROM contrib_volunteerscontributions AS ctb "
                    "LEFT JOIN geovis_singlectblayers AS lyr "
                    "ON ctb.fid = lyr.ctb "
                    f"GROUP BY {cols_str})"
                )

                case_lyr = "mt.layers"
            
            else:
                ctb_tbl = "contrib_volunteerscontributions"
                case_lyr = "NULL AS layers"
            
            q = (
                f"SELECT mt.fid, mt.pic, mt.respic, {usnamecol}"
                "to_char(mt.datehour, 'YYYY-MM-DD HH24:MI:SS') AS datehour, "
                "mt.dist, mt.direction, mt.dsun, mt.directbf, mt.orie, "
                "mt.beta, mt.gama, mt.txt, mt.pnt_name, mt.fire_name, "
                "mt.ugazimute, mt.gazimute, mt.gbfazimute, strips, "
                f"mt.photostatus, {case_lyr}, "
                "to_char(mt.datehour, 'YYYY-MM-DD') AS dateday,"
                "CAST(extract(epoch from mt.datehour) AS bigint) AS timestamp, "
                f"{place_case} AS place, {freg_case} AS fregid, "
                f"mt.cuser{selgeom}{geomc}{geombfc}{usgeom}{selgeombf} "
                f"FROM {ctb_tbl} AS mt {usjoin}"
                "LEFT JOIN georef_places AS gp "
                "ON mt.place = gp.fid "
                "LEFT JOIN georef_freguesias AS gfreg "
                "ON mt.fregid = gfreg.fid "
                f"{geomstr}{bfgeom}{whr}"
                f"{lmt}"
            )

            cols = [
                'fid', 'pic', 'respic',
                'datehour', 'dist', 'direction', 'dsun',
                'directbf', 'orie', 'beta', 'gama', 'txt',
                'pnt_name', 'fire_name', 'ugazimute',
                'gazimute', 'gbfazimute', 'strips', 'photostatus',
                'dateday', 'timestamp', 'place', 'fregid',
                'cuser', "layers"
            ]

            optcols = {
                "geom" : selgeom, "geombf" : selgeombf,
                "usergeom" : usgeom, "geomc" : geomc,
                "geombfc" : geombfc, "email": usnamecol
            }

            for c in optcols:
                if optcols[c] != '':
                    cols.append(c)
            
            cols_to_js = [f"'{c}', dtbl.{c}" for c in cols]

            fq = (
                "SELECT dateday, ARRAY_AGG(json_build_object("
                    f"{', '.join(cols_to_js)}"
                ")) AS ctbs "
                f"FROM ({q}) AS dtbl "
                "GROUP BY dateday"
            ) if orient == 'date' else q

            data = q_to_obj(db, (
                "SELECT ARRAY_AGG(row_to_json(foo)) AS data FROM ("
                f"{fq}) AS foo"
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
            'url'      : 'volu/contributions/',
            'service'  : 'manage-contributions',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fresp

    def post(self, request):
        """
        Receive Volunteer Contributions
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get request data
        rqstd = request.data

        # Get current user
        cuser  = request.user
        ustype = id_usertype(cuser)
        
        # Check if we have all data we need
        mparams = ["geom", "direction", "epsg"]
        nomandatory = [
            "orie", "gama", "beta", "txt",
            "pnt_name", "fire_name", "dsun",
            "ugazimute", "gazimute", "gbfazimute"
        ]

        _status, http = check_rqst_param(mparams, rqstd)

        # Get user if necessary
        if not _status:
            if ustype == 'superuser' and "cuser" in rqstd:
                try:
                    user = User.objects.get(pk=int(rqstd["cuser"]))
                    rqstd["cuser"] = int(user.id)
                
                except User.DoesNotExist:
                    _status, http =  {
                        "code"    : "I03",
                        "message" : "User doesn't exist"
                    }, status.HTTP_404_NOT_FOUND
            else:
                rqstd['cuser'] = int(cuser.id)

        # Sanitize request parameters
        if not _status:
            # Get photo file
            if "pic" in rqstd and rqstd['pic'] and type(rqstd["pic"]) == str:
                rqstd["pic"] = get_photo(rqstd["pic"], rqstd["cuser"])

        if not _status and "datehour" in rqstd:
            if "timezone" not in rqstd:
                _status, http = {
                    "code"    : "E01",
                    "message" : "timezone is necessary when datehour is in request"
                }, status.HTTP_400_BAD_REQUEST
        
        if not _status and "datehour" in rqstd:
            tzs = list(pytz.all_timezones)

            if rqstd["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        if not _status and "datehour" in rqstd:
            # Assign time to contribution
            df = "%Y-%m-%d %H:%M:%S"

            try:
                _tz = pytz.timezone(rqstd["timezone"])

                #check if datehour has acceptable format
                rqstd["datehour"] = dt.datetime.strptime(rqstd["datehour"], df)
                rqstd["datehour"] = _tz.localize(rqstd["datehour"])
            
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" : f'{rqstd["datehour"]} has not {df} format.'
                }, status.HTTP_400_BAD_REQUEST
        
        if not _status and "datehour" not in rqstd:
            rqstd["datehour"] = daytime
        
        if not _status:
            # Sanitize Main Geometry
            mgeom = ogr.CreateGeometryFromWkt(rqstd["geom"])

            # Project if necessary
            if rqstd["epsg"] != 3763:
                mgeom = prj_ogrgeom(mgeom, rqstd["epsg"], 3763, api='shply')
                rqstd["geom"] = mgeom.ExportToWkt()
            
            # Sanitize user geometry
            rqstd["usergeom"] = wkt_sanitize(
                rqstd["usergeom"], rgeos=True,
                epsg=3763 if rqstd["epsg"] == 3763 else rqstd["epsg"],
                reprj=None if rqstd["epsg"] == 3763 else 3763
            ) if "usergeom" in rqstd and \
                type(rqstd["usergeom"]) == str else None
            
            # Sanitize main geometry centroid
            rqstd["geomc"] = wkt_sanitize(
                rqstd["geomc"], rgeos=True,
                epsg=3763 if rqstd["epsg"] == 3763 else rqstd["epsg"],
                reprj=None if rqstd["epsg"] == 3763 else 3763
            ) if "geomc" in rqstd and \
                type(rqstd["geomc"]) == str else \
                    get_centroid(rqstd["geom"], epsg=3763, rgeos=True)

            # Set no mandatory fields
            for f in nomandatory:
                if f not in rqstd:
                    rqstd[f] = None

            # Sanitize back-front geometry
            if "geombf" not in rqstd or type(rqstd["geombf"]) != str:
                rqstd["geombf"] = None

            else:
                rqstd["geombf"] = ogr.CreateGeometryFromWkt(rqstd["geombf"])

                if rqstd["epsg"] != 3763:
                    rqstd["geombf"] = prj_ogrgeom(
                        rqstd["geombf"], rqstd["epsg"], 3763, api="shply"
                    )
            
            # Sanitize optional geometry centroid
            rqstd["geombfc"] = wkt_sanitize(
                rqstd["geombfc"], rgeos=True,
                epsg=3763 if rqstd["epsg"] == 3763 else rqstd["epsg"],
                reprj=None if rqstd["epsg"] == 3763 else 3763
            ) if "geombfc" in rqstd and \
                type(rqstd["geombfc"]) == str else \
                    get_centroid(rqstd["geombf"], epsg=3763, rgeos=True) \
                        if rqstd["geombf"] else None
            
            # MultiPoints to Points
            main_geoms = []
            for i in range(mgeom.GetGeometryCount()):
                pnt = mgeom.GetGeometryRef(i)
                pnt = wkt_sanitize(
                    pnt.ExportToWkt(), epsg=3763, rgeos=True
                )
                main_geoms.append(pnt)
            
            bf_geoms = []
            if rqstd["geombf"]:
                for i in range(rqstd["geombf"].GetGeometryCount()):
                    pnt = rqstd["geombf"].GetGeometryRef(i)
                    pnt = wkt_sanitize(
                        pnt.ExportToWkt(), epsg=3763, rgeos=True
                    )

                    bf_geoms.append(pnt)
        
            # Add contribution to table
            rqstd["strips"]      = 0
            rqstd["photostatus"] = 0
            
            srl = ContribSrl(data=rqstd)

            if srl.is_valid():
                srl.save()
                response = srl.data

            else:
                _status, http = {
                    "code"    : "Z01",
                    "message" : srl.errors
                }, status.HTTP_400_BAD_REQUEST
        
        # Record geometries
        if not _status:
            # TODO: get azimute value
            # Main geometry
            main_geoms = [{
                "pid"     : _p + 1,
                "geom"    : main_geoms[_p],
                "azimute" : 0,
                "cid"     : response["fid"] 
            } for _p in range(len(main_geoms))]

            gsrl = ContribPositionsSrl(data=main_geoms, many=True)

            if gsrl.is_valid():
                gsrl.save()

                response["geom"] = gsrl.data
            
            if bf_geoms:
                bf_geoms = [{
                    "pid"     : _p + 1,
                    "geom"    : bf_geoms[_p],
                    "azimute" : 0,
                    "cid"     : response["fid"] 
                } for _p in range(len(bf_geoms))]

                bgsrl = ContribPosistionsBackFrontSrl(data=bf_geoms, many=True)

                if bgsrl.is_valid():
                    bgsrl.save()

                    response["geombf"] = bgsrl.data
            
            else:
                response["geombf"] = None
            
            response["status"], http = {
                "code"    : "S21",
                "message" : "Contribution was received and stored",
            }, status.HTTP_201_CREATED
        
        else:
            response = {"status" : _status}

        fresp = Response(response, http)

        if "pic" in rqstd:
            rqstd["pic"] = rqstd["pic"][:10]

        # Write logs
        logi = LogsContribSrl(data={
            'url'      : 'volu/contributions/',
            'service'  : 'manage-contributions',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([
                f"{k}={str(rqstd[k])}" for k in rqstd if k != "datehour"
            ]),
            'cuser'    : cuser
        })

        if logi.is_valid(): logi.save()

        return fresp

    def delete(self, request):
        """
        Method DELETE - Delete all contributions
        ---
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get user and user type
        qp, _status, http = request.query_params, None, None
        cuser, user = request.user, None
        ustype= id_usertype(cuser)

        reftime = {"starttime" : None, "endtime" : None}

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_400_BAD_REQUEST

        # Check if starttime and endtime values are valid
        if not _status:
            for st in reftime:
                if st not in qp: continue

                try:
                    tt = dt.datetime.strptime(qp[st], '%Y-%m-%d-%H-%M-%S')

                    reftime[st] = tt

                    reftime[st] = tz.localize(reftime[st])

                except:
                    _status, http = {
                        "code"    : "E07",
                        "message" :  f"{st} has not the right format"
                    }, status.HTTP_400_BAD_REQUEST
            
                if _status: break
        
        # Check if user id is valid:
        if not _status and "userid" in qp:
            if qp["userid"] == "true":
                user = cuser
            
            else:
                isemail, usid = None, None
                try:
                    usid = int(qp["userid"])
                except ValueError:
                    isemail = True
                
                # Get user
                try:
                    user = User.objects.get(pk=usid) if not isemail \
                        else User.objects.get(username=qp["userid"])
                
                except User.DoesNotExist:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "User doesn't exist"
                    }, status.HTTP_400_BAD_REQUEST
        
        # Filter by time
        if not _status:
            if reftime["starttime"]:
                ctb = VolunteersContributions.objects.filter(
                    datehour__gte=reftime["starttime"]
                )
        
            else:
                ctb = VolunteersContributions.objects.all()
        
            if reftime["endtime"]:
                ctb = ctb.filter(datehour__lte=reftime["endtime"])
            
            # Filter by user
            if user:
                ctb = ctb.filter(cuser=user.id)

            # Delete contributions
            ctb.delete()

            response = {"status" : {
                "code"    : "S24",
                "message" : "Contributions deleted"
            }}
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write Logs
        li = LogsContribSrl(data={
            'url'      : 'volu/contributions/',
            'service'  : 'manage-contributions',
            'method'   : request.method,
            'http'     : rr.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return rr


class ManVContribution(APIView):
    """
    View, edit, delete contribution
    """

    permission_classes = [
        permissions.IsAuthenticated,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, fid):
        """
        Details of one contribution
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.query_params

        # Get user and user type
        cuser = request.user
        ustype = id_usertype(cuser)

        # Get contribution
        try:
            ctb = VolunteersContributions.objects.get(fid=int(fid))

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution doesn't exist"
            }, status.HTTP_404_NOT_FOUND

        # Check user privileges
        if not _status and ustype != 'superuser' and ustype != 'fireloc':
            if not ctb.cuser:
                _status, http = {
                    "code"    : "E03",
                    "message" : "You do not have permission to perform this action."
                }, status.HTTP_400_BAD_REQUEST

            if not _status and cuser.id != ctb.cuser.id:
                _status, http = {
                    "code"    : "E03",
                    "message" : "You do not have permission to perform this action."
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Get context object
            ctx = {
                "epsg" : None if "epsg" not in d else int(d["epsg"]),
                "geom" : True if "geom" in d and d["geom"] == "true" else None,
                "usergeom" : True if "usergeom" in d and d["usergeom"] == "true"
                    else None,
                "geombf" : True if "geombf" in d and d["geombf"] == "true"
                    else None
                #"photo"  : True if "photo" in d and d["photo"] == "true" else None
            }

            srl = ReadContrib(ctb, context=ctx)

            response = srl.data

            response["status"], http = {
                'code'    : "S20",
                'message' : "Data successfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        fresp = Response(response, status=http)

        li = LogsContribSrl(data={
            'url'      : f'volu/contribution/{str(fid)}/',
            'service'  : 'manage-contribution',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join([f"{k}={str(d[k])}" for k in d]),
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fresp

    def put(self, request, fid):
        """
        Edit Contribution data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        # Get request data
        _status, http, d = None, None, request.data

        params = [
            "pic", "respic", "datehour",
            "usergeom", "dist", "direction",
            "dsun", "directbf", "orie", "beta",
            "gama", "txt", "pnt_name", 
            "fire_name", "cuser", 
            "ugazimute", "gazimute", "gbfazimute",
            "place", "fregid", "stripgeom", "stripext"
        ]

        cuser  = request.user
        ustype = id_usertype(cuser)

        # -------------------------------- #
        # Check for errors
        # -------------------------------- #

        # Get contribution
        try:
            ctb = VolunteersContributions.objects.get(fid=int(fid))
            ctbsrl = ContribSrl(ctb)
            ctbd = ctbsrl.data

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution doesn't exist"
            }, status.HTTP_404_NOT_FOUND

        # Check user privileges
        if not _status and ustype != 'superuser' and ustype != 'fireloc'\
            and cuser.id != ctb.cuser.id:
            _status, http = {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }, status.HTTP_403_FORBIDDEN
        
        if not _status and "datehour" in d and "timezone" not in d:
            _status, http = {
                "code"    : "E01",
                "message" : "timezone is necessary when datehour is in request"
            }, status.HTTP_400_BAD_REQUEST
        
        if not _status and "datehour" in d:
            tzs = list(pytz.all_timezones)

            if d["timezone"] not in tzs:
                _status, http = {
                    "code"    : "E08",
                    "message" : "timezone is invalid"
                }, status.HTTP_400_BAD_REQUEST
        
        # Check datetime format
        if not _status and 'datehour' in d:
            df = "%Y-%m-%d %H:%M:%S"
            try:
                _tz = pytz.timezone(d["timezone"])

                #check if datehour has acceptable format
                d['datehour'] = dt.datetime.strptime(d["datehour"], df)
                d['datehour'] = _tz.localize(d["datehour"])
                    
            except:
                _status, http = {
                    "code"    : "E07",
                    "message" : f'datehour has not {df} format.'
                }, status.HTTP_400_BAD_REQUEST
        
        # Check if we have epsg
        geoms_fields = [
            "geom", "usergeom", "geombf", "geomc", "geombfc",
            "stripgeom", "stripext"
        ]
        if not _status and any(i in d for i in geoms_fields) and \
            "epsg" not in d:
            _status, http = {
                "code"    : "E01",
                "message" : "EPSG is not in request"
            }, status.HTTP_400_BAD_REQUEST

        # Check if we have geom/geombf and azimutes
        # Both collections must have the same dimension
        gf = {"geom" : "geom_az", "geombf" : "geombf_az"}

        if not _status:
            for k in gf:
                if k not in d: continue

                gobj = ogr.CreateGeometryFromWkt(d[k])

                if d["epsg"] != 3763:
                    gobj = prj_ogrgeom(gobj, d["epsg"], 3763, api="shply")
                
                ngeom = gobj.GetGeometryCount()

                if gf[k] in d:
                    naz = len(d[gf[k]])

                    if ngeom != naz:
                        _status, http = {
                            "code"    : "E09",
                            "message" : f"{k} and {gf[k]} need to have the same dimension"
                        }, status.HTTP_400_BAD_REQUEST
                else:
                    naz = None
                
                if _status: break
            
                d[f"{k}_data"] = []

                for i in range(ngeom):
                    pnt = gobj.GetGeometryRef(i)
                    pnt = wkt_sanitize(pnt.ExportToWkt(), epsg=3763, rgeos=True)

                    d[f"{k}_data"].append({
                        "pid"     : i + 1,
                        "geom"    : pnt,
                        "azimute" : 0 if not naz else int(round(d[gf[k]][i])),
                        "cid"     : ctbd["fid"]
                    })
        
        # -------------------------------- #

        # -------------------------------- #
        # Update Contribution part
        # -------------------------------- #
        
        # Update pic
        if not _status and "pic" in d and d["pic"]:
            # Get Photo file
            d["pic"] = get_photo(d["pic"], ctb.cuser.id, ctb=fid)
        
        if not _status and "respic" in d and d["respic"]:
            d["respic"] = get_photo(
                d["respic"], ctb.cuser.id,
                resphoto=True, ctb=fid
            )
        
        # Update Geometry
        geomd = {}
        if not _status:
            for g in gf:
                if g not in d: continue

                M = VolunteersPositions if g == "geom" else \
                    VolunteersPositionsBackFront
                
                S = ContribPositionsSrl if g == "geom" else \
                    ContribPosistionsBackFrontSrl
                
                cpos = M.objects.filter(cid=ctbd["fid"])

                cpos.delete()

                gsrl = S(data=d[f"{g}_data"], many=True)

                if gsrl.is_valid():
                    gsrl.save()

                    geomd[g] = gsrl.data

        # Get data
        if not _status:
            for p in params:
                if p not in d:
                    d[p] = ctbd[p]
                    continue
            
                if p == 'cuser':
                    d[p] = ctbd['cuser']
                    continue
                
                if (p == "usergeom" or p == "geomc" or p == "geombfc" or \
                    p == 'stripgeom' or p == 'stripext'):
                    d[p] = wkt_sanitize(
                        d[p], rgeos=True,
                        epsg=3763 if d["epsg"] == 3763 else d["epsg"],
                        reprj=None if d["epsg"] == 3763 else 3763
                    ) if d[p] else None

                if p == 'place':
                    try:
                        _place = Places.objects.get(pk=d[p])
                    except Places.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "Place doesn't exist."
                        }, status.HTTP_404_NOT_FOUND

                if p == 'fregid':
                    try:
                        _freg = Freguesias.objects.get(code=d[p])
                        d[p] = _freg.fid
                    except Freguesias.DoesNotExist:
                        _status, http = {
                            "code"    : "I03",
                            "message" : "Freguesia doesn't exist."
                        }, status.HTTP_404_NOT_FOUND

        if not _status:
            srl = ContribSrl(ctb, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                for k in geomd:
                    response[k] = geomd[k]
                    
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Contribution was edited",
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
            
        else:
            response = {"status" : _status}
        
        fresp = Response(response, status=http)

        _d = [f"{k}={str(d[k])}" for k in d \
            if k != 'geom' and k != 'geombf' and k != 'stripgeom'\
                and k != "stripext"]
        li = LogsContribSrl(data={
            'url'      : f'/volu/contribution/{str(fid)}/',
            'service'  : 'manage-contribution',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : ";".join(_d),
            'cuser'    : cuser.pk
        })

        if li.is_valid(): li.save()

        return fresp

    def delete(self, request, fid):
        """
        Delete contribution
        """
        
        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        # Get user and user type
        cuser = request.user
        ustype = id_usertype(cuser)

        # Get contribution
        try:
            ctb = VolunteersContributions.objects.get(fid=int(fid))

        except VolunteersContributions.DoesNotExist:
            _status, http =  {
                "code"    : "I01",
                "message" : "Contribution does not exist"
            }, status.HTTP_404_NOT_FOUND

        # Check user privileges
        if not _status and ustype != 'superuser' and ustype != 'fireloc':
            if not ctb.cuser:
                _status, http = {
                    "code"    : "E03",
                    "message" : "You do not have permission to perform this action."
                }, status.HTTP_400_BAD_REQUEST

            if not _status and cuser.id != ctb.cuser.id:
                _status, http = {
                    "code"    : "E03",
                    "message" : "You do not have permission to perform this action."
                }, status.HTTP_400_BAD_REQUEST

        if not _status:
            # Handle pic name
            pic = str(ctb.pic)[:-1].split("/")[-1]

            # Delete photo if exists
            photofld = GEOMEDIA_FOLDERS.get("CTB_PHOTOS", None)

            path = os.path.join(photofld, pic)

            photos = lst_ff(photofld, rfilename=True)

            if pic in photos:
                # Delete contribution
                del_file(path)
            
            ctb.delete()

            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Contribution was deleted"
            }}, status.HTTP_202_ACCEPTED

        else:
            response = {"status" : _status}

        fresp = Response(response, status=http)

        # Write logs
        logi = LogsContribSrl(data={
            'url'      : f'volu/contribution/{str(fid)}/',
            'service'  : 'manage-contribution',
            'method'   : request.method,
            'http'     : fresp.status_code,
            'code'     : response["status"]["code"],
            'message'  : response["status"]["message"],
            'datehour' : daytime,
            'data'     : None,
            'cuser'    : cuser.pk
        })

        if logi.is_valid(): logi.save()

        return fresp

