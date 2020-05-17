"""
List Statistic Unities By Country
"""

from rest_framework import generics

"""
Countries data as HTTP Response
"""
from weapi.models       import Countries
from weapi.serial.lstsu import CountriesSerializer
class StatUnitsList(generics.ListAPIView):
    #queryset = countries.objects.all()
    serializer_class = CountriesSerializer
    
    def get_queryset(self):
        __limit = self.request.query_params.get('limit')
        
        if __limit:
            return Countries.objects.all()[:int(__limit)]
        else:
            return Countries.objects.all()

