"""
List Themes/Indicators
"""

from rest_framework import serializers

"""
Serializer for Indicators
"""
from weapi.models import ThemeLyr
class ListIndicators(serializers.ModelSerializer):
    class Meta:
        model  = ThemeLyr
        fields = ("fid", "slug", "name")

