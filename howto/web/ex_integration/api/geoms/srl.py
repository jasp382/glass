"""
Models Serializers
"""

from rest_framework import serializers

from geoms.models import Geodata


class GeodataSrl(serializers.ModelSerializer):
    class Meta:
        model = Geodata
        fields = ["id", "code", "name", "geom", "layerid"]

