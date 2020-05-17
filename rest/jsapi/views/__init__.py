from rest_framework import generics

""" View for Geoserver Connection """
from weapi.models import GeoServerCon
from weapi.serial import GeoserverParam

class GetGeoServerCon(generics.ListAPIView):
    serializer_class = GeoserverParam
    
    def get_queryset(self):
        return GeoServerCon.objects.filter(fid=1)


"""
Data in View as HTTP Response
"""
def view_via_api(request, view):
    """
    View in Database to Response
    """
    
    import json
    from gasp3.sql.fm   import Q_to_df
    from wgeng.settings import DATABASES
    from django.http    import JsonResponse
    
    if 'fields' in request.GET:
        cols = request.GET['fields']
    else:
        cols = "*"
    
    df = Q_to_df(
        DATABASES['default'], "SELECT {} FROM {}".format(cols, view)
    )
    
    data = json.loads(df.to_json(orient='records'))
    
    return JsonResponse(data, safe=False)


""" List Years in Database """
from weapi.models import Years
from weapi.serial import ListYears
class YearsView(generics.ListAPIView):
    queryset = Years.objects.all()
    serializer_class = ListYears


"""
Data Upload data Info as HTTP Response
"""
from weapi.models import UploadData, UploadCols
from weapi.serial import ListDatasetCols, ListDatasets

class ListDatasetsById(generics.ListAPIView):
    #queryset = upload_data.objects.all()
    serializer_class = ListDatasets
    
    def get_queryset(self):
        from django.db.models import Q
        
        #__fid = self.kwargs['fid']
        __fid = self.request.query_params.get('fid')
        
        if __fid:
            return UploadData.objects.filter(fid=__fid)
        
        else:
            return UploadData.objects.all()


class ListColsById(generics.ListAPIView):
    #queryset = upload_cols.objects.all()
    serializer_class = ListDatasetCols
    
    def get_queryset(self):
        from django.db.models import Q
        
        __fid = self.request.query_params.get('fid')
        __ctx = self.request.query_params.get('ctx')
        
        if __fid and not __ctx:
            return UploadCols.objects.filter(rqst_id=__fid)
        
        elif not __fid and __ctx:
            __ctx = True if int(__ctx) == 1 else False
            
            return UploadCols.objects.filter(ctx_col=__ctx)
        
        elif __fid and __ctx:
            __ctx = True if int(__ctx) == 1 else False
            
            return UploadCols.objects.filter(
                Q(rqst_id=__fid) & Q(ctx_col=__ctx)
            )
        
        else:
            return UploadCols.objects.all()


"""
Delete All Data Table
"""
def del_table(request, table):
    """
    Delete Table data
    """
    
    from django.http import HttpResponse
    from gasp3 import __import
    
    mdl = __import('weapi.models.{}'.format(table))
    
    mdl.objects.all().delete()
    
    return HttpResponse('success')