"""
List Study Cases
"""

from rest_framework import generics

"""
Study Cases data as HTTP Response
"""
from weapi.serial.lstcase import CasesSerializer
from weapi.models import StudyCases

class ListCasesView(generics.ListAPIView):
    serializer_class = CasesSerializer
    
    def get_queryset(self):
        return StudyCases.objects.all()


"""
Indicators Layers in Study Case
"""
from weapi.models import LyrIndicators
from weapi.serial.lstlyr import ListIndicatorLyr
class IndicatorsLyrView(generics.ListAPIView):
    serializer_class = ListIndicatorLyr
    
    def get_queryset(self):
        from django.db.models import Q
        __case     = self.request.query_params.get('case')
        __year     = self.request.query_params.get('year')
        
        if __case and not __year:
            return LyrIndicators.objects.filter(id_case=__case)
        
        elif not __case and __year:
            return LyrIndicators.objects.filter(id_year=__year)
        
        elif __case and __year:
            return LyrIndicators.objects.filter(
                Q(id_case=__case) & Q(id_year=__year)
            )
        
        else:
            return LyrIndicators.objects.all()

from weapi.models        import Years
from weapi.serial.lstlyr import ListLyrByYear
class IndicatorLyrByYear(generics.ListAPIView):
    serializer_class = ListLyrByYear
    
    def get_queryset(self):
        from django.db.models.aggregates import Count
        from django.db.models import Q
        
        __case = self.request.query_params.get('case')
        
        if __case:
            return Years.objects.filter(
                lyr_year__id_case=__case
            ).annotate(n=Count("year"))
        
        else:
            return Years.objects.all()


"""
Point Layers in Study Cases
"""

from weapi.models        import PntLyr
from weapi.serial.lstlyr import PntLyrSerial

class PntLyrLst(generics.ListAPIView):
    serializer_class = PntLyrSerial
    
    def get_queryset(self):
        __case = self.request.query_params.get('case')
        
        if __case:
            return PntLyr.objects.filter(idcase=__case)
        else:
            return PntLyr.objects.all()


"""
Polygon Layers in Study Cases
"""
from weapi.models import PolygonLyr
from weapi.serial.lstlyr import PolyLyrSerial

class PolyLyrLst(generics.ListAPIView):
    serializer_class = PolyLyrSerial
    
    def get_queryset(self):
        __case = self.request.query_params.get('case')
        
        if __case:
            return PolygonLyr.objects.filter(fidcase=__case)
        
        else:
            return PolygonLyr.objects.all()

