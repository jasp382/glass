"""
Views to manage Geocharts data
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

from firerest.permcls  import IsFireloc
from firerest.utils import check_rqst_param
from authapi.utils import id_usertype

from geovis.models import GeoCharts, ChartsSeries, ChartsData
from geovis.srl import GeoChartSrl, GeoChartSerieSrl, GeoChartDataSrl

from logs.srl import LogsGeovisSrl


class ManGeoCharts(APIView):
    """
    Manage GeoCharts and their series
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request):
        """
        Method GET - Retrieve all existing charts
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)
        
        code, msg = "S20", "Data successfully returned"

        charts = GeoCharts.objects.all()
        srl = GeoChartSrl(charts, many=True)

        response, http = {
            "status" : {"code" : code, "message" : msg},
            "data"   : srl.data
        }, status.HTTP_200_OK

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : 'geo-charts/',
            'service'  : 'manage-geo-charts',
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
        Method POST - Add new chart and series
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d = request.data

        ctypes = ["BAR", "LINE", "PIE", "SCATTER"]

        pp = [
            "slug", "designation","description", "chartype",
            "serieslugs", "seriesnames", "seriescolors"
        ]
        
        _status, http = check_rqst_param(pp, list(d.keys()))

        # Check chartype value
        if not _status and d["chartype"] not in ctypes:
            _status, http = {
                "code"    : "E06",
                "message" : "chartype value is not valid"
            }, status.HTTP_400_BAD_REQUEST
        
        # Check series names and seriescolors
        if not _status:
            slugs   = obj_to_lst(d["serieslugs"])
            snames  = obj_to_lst(d['seriesnames'])
            scolors = obj_to_lst(d['seriescolors'])

            if len(slugs) != len(snames) or len(snames) != len(scolors):
                _status, http = {
                    "code"    : "E09",
                    "message" : "serieslugs, seriesnames and seriescolors must have same length"
                }, status.HTTP_400_BAD_REQUEST

        #Handling Charts
        if not _status:
            chartsrl = GeoChartSrl(data=d)
            
            if chartsrl.is_valid():
                chartsrl.save()

                response = chartsrl.data

                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Chart and its series created."
                }, status.HTTP_201_CREATED
        
            else:
                _status, http = {
                    "code"    : "Z01", 
                    "message" : str(chartsrl.errors)
                }, status.HTTP_400_BAD_REQUEST

        #Handling Chart Series
        if not _status:
            series = []
            for i in range(len(snames)):
                series.append({
                    "chartid" : response["id"],
                    "slug"    : slugs[i],
                    "name"    : snames[i],
                    "color"   : scolors[i]
                })
            
            srl = GeoChartSerieSrl(data=series, many=True)

            if srl.is_valid():
                srl.save()

                response["series"] = srl.data
    
            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : 'geovis/geo-charts/',
            'service'  : 'manage-geo-charts',
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
    
    def delete(self, request):
        """
        Method DELETE - Delete all charts
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

         # Get user and user type
        cuser = request.user
        ustype, _status = id_usertype(cuser), None

        # Check user privileges
        if ustype != 'superuser':  
            _status, http = {"status" : {
                "code"    : "E03",
                "message" : "You do not have permission to perform this action."
            }}, status.HTTP_400_BAD_REQUEST
        
        if not _status:
            # Delete data
            GeoCharts.objects.all().delete()
            
            _status, http = {"status" : {
                "code"    : "S24",
                "message" : "Geo Charts deleted"
            }}, status.HTTP_200_OK

        response = _status

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : 'geovis/geo-charts/',
            'service'  : 'manage-geo-charts',
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


class ManGeoChart(APIView):
    """
    Manage GeoChart and their series
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]

    def get(self, request, chartid):
        """
        Method GET - Retrieve chart data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            chart = GeoCharts.objects.get(slug=chartid)
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Geo Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND
 
        if not _status:
            srl = GeoChartSrl(chart)

            response = srl.data
            
            response["status"], http = {
                "code"    : "S20",
                "message" : "Data sucessfully returned"
            }, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart/{str(chartid)}/',
            'service'  : 'manage-geo-chart',
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
    

    def put(self, request, chartid):
        """
        Method PUT - update existing chart and it series
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        warns, slugs, snames, colors = [], [], [], []
        series = []

        ctypes = ["BAR", "LINE", "PIE", "SCATTER"]

        rp = ["slug", "designation", "description", "chartype"]

        '''
        Handling Chart Serializer Data
        '''
        try:
            chart = GeoCharts.objects.get(slug=chartid)
            srl = GeoChartSrl(chart)
            srldata = srl.data
        
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Geo Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        # Check chartype value
        if not _status and "chartype" in d and d["chartype"] not in ctypes:
            _status, http = {
                "code"    : "E06",
                "message" : "chartype value is not valid"
            }, status.HTTP_400_BAD_REQUEST
        
        '''
        Handling Chart Serie Serializer Data
        '''
        if not _status:
            if 'serieslugs' in d:
                slugs.extend(obj_to_lst(d["serieslugs"]))

                if 'seriesnames' in d:
                    snames.extend(obj_to_lst(d["seriesnames"]))

                if 'seriescolors' in d:
                    colors.extend(obj_to_lst(d["seriescolors"]))
                
                if len(slugs) != len(snames):
                    _status, http = {
                        "code"    : "E09",
                        "message" : "serieslugs and seriesnames must have same length"
                    }, status.HTTP_400_BAD_REQUEST
                
                if len(slugs) != len(colors):
                    _status, http = {
                        "code"    : "E09",
                        "message" : "serieslugs and seriescolors must have same length"
                    }, status.HTTP_400_BAD_REQUEST
            else:
                if 'seriesnames' in d or 'seriescolors' in d:
                    warns.append("Series names and colors will not be added without serieslugs")
        
        if not _status and len(slugs):
            # Get series object and update it
            # Create a new one if it doesn't exist
            for s in range(len(slugs)):
                _d = {
                    "slug"    : slugs[s],
                    "name"    : snames[s] if snames else None,
                    "color"   : colors[s] if colors else None,
                    "chartid" : chart.id
                }
                try:
                    sobj = ChartsSeries.objects.get(slug=slugs[s])

                    ssrl = GeoChartSerieSrl(sobj, data=_d)

                    if ssrl.is_valid():
                        ssrl.save()

                        series.append(ssrl.data)
                
                except ChartsSeries.DoesNotExist:
                    # Add new value if we have colors and names
                    if not snames or not colors:
                        warns.append(
                            f"series {slugs[s]} will not be create without colors and names"
                        )
                        continue

                    ssrl = GeoChartSerieSrl(data=_d)

                    if ssrl.is_valid():
                        ssrl.save()

                        series.append(ssrl.data)
                
                except ChartsSeries.MultipleObjectsReturned:
                    # Error - multiple objects are not possible
                    _status, http = {
                        "code"    : "I04",
                        "message" : "This chart has more than one series with the same slug"
                    }, status.HTTP_400_BAD_REQUEST

        # Get Chart attrs values
        if not _status:
            for p in rp:
                if p not in d:        
                    d[p] =  srldata[p]
     
            srl = GeoChartSrl(chart, data=d)

            if srl.is_valid():
                srl.save()

                response = srl.data

                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Chart and it's series were updated."
                }, status.HTTP_201_CREATED

                response["series"] = series
            
            else:
                response, http = {"status" : {
                    "code"    : "Z01",
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        
        else:
            response = {"status" : _status}     

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart/{str(chartid)}/',
            'service'  : 'manage-geo-chart',
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
    
    def delete(self, request, chartid):
        """
        Method DELETE - Delete one chart
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None
        
        try:
            chart = GeoCharts.objects.get(slug=chartid)
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I01",
                "message" : "Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND
        
        if not _status:
            chart.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Chart and it serie deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}
        
        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart/{str(chartid)}/',
            'service'  : 'manage-geo-chart',
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


class ManChartData(APIView):
    """
    Manage data of a Chart|Series
    """

    permission_classes = [
        permissions.IsAdminUser|IsFireloc,
        TokenHasReadWriteScope
    ]
    parser_classes = [JSONParser]
    
    def post(self, request, chartid, seriesid):
        """
        Method POST - Add data of a chart|series
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        d, pp = request.data, ["x", "y"]
        _status, http = check_rqst_param(pp, list(d.keys()))

        try:
            chart = GeoCharts.objects.get(slug=chartid)
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I03",
                "message" : "Geo Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            try:
                serie = ChartsSeries.objects.get(slug=seriesid)

                if chart.id != serie.chartid:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Given series is not part of the given chart"
                    }, status.HTTP_400_BAD_REQUEST 

            except ChartsSeries.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Geo Serie doesn't exist."
                }, status.HTTP_404_NOT_FOUND

        # Check x, y lengths
        if not _status:
            x, y = obj_to_lst(d['x']), obj_to_lst(d['y'])

            if len(x) != len(y):
                  _status, http = {
                    "code"    : "E09",
                    "message" : "X and Y must have the same length"
                }, status.HTTP_400_BAD_REQUEST 

        if not _status:
            _d = [{
                "xvalue" : x[i],
                "yvalue" : y[i],
                'sid'    : serie.id
            } for i in range(len(x))]

            srl = GeoChartDataSrl(data=_d, many=True)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S21",
                    "message" : "New Chart|Serie Data added."
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST
        else:
            response = {"status" : _status}   


        rr = Response(response, status=http)
        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart-data/{str(chartid)}/{str(seriesid)}/',
            'service'  : 'manage-geo-chart-data',
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
    
    def put(self, request, chartid, seriesid):
        """
        Method PUT - Update data of a chart|series
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http, d = None, None, request.data

        rp = ["x", 'y']

        try:
            chart = GeoCharts.objects.get(slug=chartid)
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I03",
                "message" : "Geo Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            try:
                serie = ChartsSeries.objects.get(slug=seriesid)

                if chart.id != serie.chartid:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Given series is not part of the given chart"
                    }, status.HTTP_400_BAD_REQUEST 
                
            except ChartsSeries.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Geo Serie doesn't exist."
                }, status.HTTP_404_NOT_FOUND 

          # Check x, y lengths
        if not _status:
            x, y = obj_to_lst(d['x']), obj_to_lst(d['y'])

            if len(x) != len(y):
                  _status, http = {
                    "code"    : "E09",
                    "message" : "X and Y must have the same length"
                }, status.HTTP_400_BAD_REQUEST 

        if not _status:
            cdat = ChartsData.objects.filter(sid=serie.id)
            cdat.delete()

            _d = [{
                "xvalue" : x[i],
                "yvalue" : y[i],
                'sid'    : serie.id
            } for i in range(len(x))]

            srl = GeoChartDataSrl(data=_d, many=True)

            if srl.is_valid():
                srl.save()

                response = srl.data
                
                response["status"], http = {
                    "code"    : "S22",
                    "message" : "Chart|Serie Data was updated."
                }, status.HTTP_201_CREATED

            else:
                response, http = {"status" : {
                    "code"    : "Z01", 
                    "message" : str(srl.errors)
                }}, status.HTTP_400_BAD_REQUEST

        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart-data/{str(chartid)}/{str(seriesid)}/',
            'service'  : 'manage-geo-chart-data',
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
    
    def delete(self, request, chartid, seriesid):
        """
        Method DELETE - Delete data
        """

        tz       = pytz.timezone('UTC')
        _daytime = dt.datetime.utcnow().replace(microsecond=0)
        daytime  = tz.localize(_daytime)

        _status, http = None, None

        try:
            chart = GeoCharts.objects.get(slug=chartid)
        except GeoCharts.DoesNotExist:
            _status, http = {
                "code"    : "I03",
                "message" : "Geo Chart doesn't exist."
            }, status.HTTP_404_NOT_FOUND

        if not _status:
            try:
                serie = ChartsSeries.objects.get(slug=seriesid)

                if chart.id != serie.chartid:
                    _status, http = {
                        "code"    : "I03",
                        "message" : "Given series is not part of the given chart"
                    }, status.HTTP_400_BAD_REQUEST 
            
            except ChartsSeries.DoesNotExist:
                _status, http = {
                    "code"    : "I03",
                    "message" : "Geo Serie doesn't exist."
                }, status.HTTP_404_NOT_FOUND 
        
        if not _status:
            cdata = ChartsData.objects.filter(sid=serie.id)
            cdata.delete()
            
            response, http = {"status" : {
                "code"    : "S23",
                "message" : "Chart|Serie Data deleted"
            }}, status.HTTP_200_OK
        
        else:
            response = {"status" : _status}

        rr = Response(response, status=http)

        # Write logs
        logsrl = LogsGeovisSrl(data={
            'url'      : f'geo-chart-data/{str(chartid)}/{str(seriesid)}/',
            'service'  : 'manage-geo-chart-data',
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

