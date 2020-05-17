"""
Serializers For Study Cases
"""

from rest_framework import serializers

"""
Serializer for Study Cases
"""
from weapi.models  import StudyCases

class CasesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCases
        fields = ("fid", "slug", "descricao", "top", "bottom", "left", "right")

