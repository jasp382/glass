"""
Meteo Serializers
"""

from rest_framework import serializers

from meteo.models import MeteoObservation, MeteoSource
from meteo.models import MeteoStation, MeteoVariables
from meteo.models import MeteoObservationValues, MeteoForecast
from meteo.models import MeteoForecastValues

class MeteoObSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoObservation
        fields = ["id", "date", "station"]

class MeteoForecSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoForecast
        fields = ["id", "date", "geom"]


class MeteoSrcSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoSource
        fields = [
            "id", "slug", "name", "description",
            "url", "token"
        ]

class MeteoStatSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoStation
        fields = [
            "id", "idapi", "name", "geom"
        ]

class MeteoVarSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoVariables
        fields = [
            "id", "slug", "name", "description",
            "unit", "source"
        ]

class MeteoObsValSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoObservationValues
        fields = [
            "id", "value", "obsid", "varid"
        ]

class MeteoForecValSrl(serializers.ModelSerializer):
    class Meta:
        model = MeteoForecastValues
        fields = [
            "id", "value", "forecid", "varid"
        ]
