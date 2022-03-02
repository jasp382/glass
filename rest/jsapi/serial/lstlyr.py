"""
REST API Serializers for Lists
"""

from rest_framework import serializers

"""
Serializer for Points Layer
"""
from weapi.models import StudyCases, PntCols, PntLyr

class PntColsSerial(serializers.ModelSerializer):
    class Meta:
        model = PntCols
        fields = ("name",)


class PntLyrSerial(serializers.ModelSerializer):
    cols = PntColsSerial(many=True, read_only=True)
    
    class Meta:
        model = PntLyr
        fields = ("fid", "name", "icon", "idcase", "cols")


"""
Serializer for Polygons Layer
"""
from weapi.models import PolygonLyr
class PolyLyrSerial(serializers.ModelSerializer):
    class Meta:
        model = PolygonLyr
        fields = ("fid", "name", "fidcase")


"""
Serializer for Layers
"""
from weapi.serial import ListYears
from weapi.serial.lstindicator import ListIndicators
from weapi.models import LyrIndicators, LyrIndicatorsCls, IndValues

class ListLyrCls(serializers.ModelSerializer):
    class Meta:
        model  = LyrIndicatorsCls
        fields = ('order', 'cat_val', 'color', 'ctx_val')
 
class ListValues(serializers.ModelSerializer):
     class Meta:
         model = IndValues
         fields = ("id_unit", "value", "cls")
 
class ListIndicatorLyr(serializers.ModelSerializer):
    #id_case = CasesSerializer()
    lyr_cls      = ListLyrCls(many=True, read_only=True)
    id_year      = ListYears()
    id_indicator = ListIndicators()
    lyr_vals     = ListValues(many=True, read_only=True)
    
    class Meta:
        model = LyrIndicators
        fields = ("fid", "id_case", "id_indicator", "id_year",
                  "lyr_cls", "lyr_vals",
                  "min_val", "max_val", "mean_val", "style")

# List Indicators Layer By Year
from weapi.models import Years
class ListLyrByYear(serializers.ModelSerializer):
    lyr_year = ListIndicatorLyr(many=True, read_only=True)
    
    class Meta:
        model = Years
        fields = ("fid", "year", "lyr_year")

