"""
Views to Manage styles
"""

from rest_framework import generics

"""
List Styles View
"""
from weapi.serial.lststyle import SldStylesSerial
from weapi.models import SldStyles
class ListStyles(generics.ListAPIView):
    serializer_class = SldStylesSerial
    
    def get_queryset(self):
        return SldStyles.objects.all()

