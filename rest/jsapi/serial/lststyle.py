"""
Styles
"""
from rest_framework import serializers

"""
Serializer for SLD Rules
"""
from weapi.models import SldRules

class SldRulesSerial(serializers.ModelSerializer):
    class Meta:
        model = SldRules
        fields = ("red", "green", "blue", "opacity", "order",
                  "quality", "stk_red", "stk_green", "stk_blue")


"""
Serializer for SLD Styles
"""

from weapi.models import SldStyles
class SldStylesSerial(serializers.ModelSerializer):
    sldrules = SldRulesSerial(many=True, read_only=True)
    
    class Meta:
        model = SldStyles
        fields = ("fid", "name", "sldrules")

