"""
Logs Serializers
"""

from rest_framework import serializers

from logs.models import LogsGeosat, LogsGeovis, LogsToken
from logs.models import LogsGeoRef, LogsSdi, LogsEvents
from logs.models import LogsGeoRst, LogsAuth, LogsContrib 
from logs.models import LogsFiredetect, LogsMeteo, LogsGeoVec


class LogsTokenSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsToken
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsAuthSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsAuth
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsContribSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsContrib
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsEventSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsEvents
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsSDISrl(serializers.ModelSerializer):
    class Meta:
        model = LogsSdi
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsGeoRefSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsGeoRef
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method"
        )


class LogsGeoRstSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsGeoRst
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsGeovisSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsGeovis
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsFiredetectSrl(serializers.ModelSerializer):
    class Meta:
        model  = LogsFiredetect
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsGeosatSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsGeosat
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )

class LogsMeteoSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsMeteo
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )


class LogsVecSrl(serializers.ModelSerializer):
    class Meta:
        model = LogsGeoVec
        fields = (
            "fid", "url", "service", "http",
            "code", "message", "datehour", "data",
            "method", "cuser"
        )

