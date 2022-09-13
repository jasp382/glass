"""
REST API Serializers
"""

from rest_framework import serializers

"""
Serializer for Statistic Units
"""
from weapi.models import StatUnit
class StatUnitSerial(serializers.ModelSerializer):
    class Meta:
        model = StatUnit
        fields = ("id_unit", "design", "scale")


"""
Serializer for Countries
"""
from weapi.models import Countries, Scale

class StatsSerializerFields(serializers.ModelSerializer):
    """
    Set fields of Countries Serializer
    """
    
    def __init__(self, *args, **kwargs):
        super(StatsSerializerFields, self).__init__(*args, **kwargs)
        
        fields = self.context['request'].query_params.get('fields')
        
        if fields:
            fields = fields.split(',')
            # Drop any fields not in `fields`
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Scale
        fields = ("fid", "desig")


class CountriesSerializer(StatsSerializerFields, serializers.ModelSerializer):
    stats = StatUnitSerial(many=True, read_only=True)
    scale = ScaleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Countries
        fields = ("fid", "slug", "descricao", "stats", "scale")
