from rest_framework import serializers

from geovis.models import MapLayers, MapLayerAttr
from geovis.models import ClusterLayers
from geovis.models import MapsLegend, GeoCharts
from geovis.models import ChartsSeries, ChartsData
from geovis.models import MapFireAss, FireMapLeg
from geovis.models import EventsLayers, EventsMapLeg
from geovis.models import SingleCtbLayers
from geovis.models import PermLayers


class MapFireSrl(serializers.ModelSerializer):
    class Meta:
        model = MapFireAss
        fields = [
            "id", "slug", "work", "design",
            "store", "glyr", "style", "flocid",
            "datehour"
        ]

class MapRFireSrl(serializers.ModelSerializer):
    class Meta:
        model = EventsLayers
        fields = [
            "id", "slug", "work", "design",
            "store", "glyr", "style", "fireid"
        ]


class LayerAttrSrl(serializers.ModelSerializer):
    class Meta:
        model = MapLayerAttr
        fields = ["id","slug","label","layerid"]

class MapLayersSrl(serializers.ModelSerializer):
    lyrattr = LayerAttrSrl(many=True, read_only=True)
    child = serializers.SerializerMethodField()

    class Meta:
        model = MapLayers
        fields = [
            "id", "slug", "designation", "workspace",
            "store", "gsrvlyr", "style", "lyrattr",
            "rootid", "level", "child"
        ]
    
    def get_child(self, obj):
        astree = self.context.get("astree", None)

        if not astree: return None
        
        childs = MapLayers.objects.filter(rootid=obj.id)

        srl = MapLayersSrl(childs, many=True, context=self.context)

        return srl.data if len(srl.data) else None


class MapLegSrl(serializers.ModelSerializer):
    class Meta:
        model = MapsLegend
        fields = (
            "cat", "minval", "maxval", "color",
            "label", "order", "layerid"
        )


class FireMapLegSrl(serializers.ModelSerializer):
    class Meta:
        model = FireMapLeg
        fields = (
            "cat", "minval", "maxval", "color",
            "label", "order", "lyrid"
        )


class RealFireLegSrl(serializers.ModelSerializer):
    class Meta:
        model = EventsMapLeg
        fields = (
            "cat", "minval", "maxval", "color",
            "label", "order", "lyrid"
        )


class GeoChartSerieSrl(serializers.ModelSerializer):
    class Meta:
        model = ChartsSeries
        fields = ["id", "slug", "color", "name", "chartid"]


class GeoChartSrl(serializers.ModelSerializer):
    series = GeoChartSerieSrl(many=True, read_only=True)

    class Meta:
        model = GeoCharts
        fields = [
            "id", "slug", "designation", 
            "description", "chartype", "series"
        ]


class GeoChartDataSrl(serializers.ModelSerializer):
    class Meta:
        model = ChartsData
        fields = ["id", "xvalue", "yvalue", "sid"]


class ClusterLayersSrl(serializers.ModelSerializer):
    geojson = serializers.SerializerMethodField('get_geojson')
    leaflyr = serializers.SerializerMethodField('get_leaflyr')

    class Meta:
        model = ClusterLayers
        fields = [
            "id", "slug", "designation", "workspace",
            "store", "gsrvlyr", 
            "eps", "minzoom", "maxzoom", "minpts",
            "level", "geojson", "leaflyr"
        ]
    
    def get_geojson(self, obj): return None
    
    def get_leaflyr(self, obj): return False


class PermLyrSrl(serializers.ModelSerializer):
    class Meta:
        model = PermLayers
        fields = [
            "id", "slug", "designation",
            "workspace", "store", "gsrvlyr",
            "query"
        ]


class SCtbLyrSrl(serializers.ModelSerializer):
    class Meta:
        model = SingleCtbLayers
        fields = [
            "id", "slug", "desig", "work",
            "store", "layer", "wms", "ctb", "style"
        ]

