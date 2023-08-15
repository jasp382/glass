from rest_framework import serializers
from georst.models import RasterTypes, RasterDatasets, RasterLayers


class RasterTypeSrl(serializers.ModelSerializer):
    class Meta:
        model = RasterTypes
        fields = ["id", "slug", "name", "description"]


class RasterDatasetSrl(serializers.ModelSerializer):
    class Meta:
        model = RasterDatasets
        fields = [
            "id", "slug", "name", "description", "source",
            "idtype", "refprod", "refyear"    
        ]


class RasterLayerSrl(serializers.ModelSerializer):
    class Meta:
        model = RasterLayers
        fields = [
            "id", "layer", "cellsizex", "cellsizey", 
            "method", "level", "refgrid", 
            "idrst"
        ]
