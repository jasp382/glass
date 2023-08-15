from rest_framework import serializers

from geovec.models import VectorCat, VectorDatasets, VectorLevels

class VecCatSrl(serializers.ModelSerializer):
    class Meta:
        model = VectorCat
        fields = ["id", "slug", "name", "description"]


class VectorLevelsSrl(serializers.ModelSerializer):
    class Meta:
        model = VectorLevels
        fields = [
            "id", "slug", "name", "description",
            "level", "dsetid"
        ]


class VectorDsetSrl(serializers.ModelSerializer):
    dsetlevel = VectorLevelsSrl(many=True, read_only=True)

    class Meta:
        model = VectorDatasets
        fields = [
            "id", "slug", "name", "description",
            "refyear", "refprod", "source",
            "gtype", "catid", "dsetlevel"
        ]

