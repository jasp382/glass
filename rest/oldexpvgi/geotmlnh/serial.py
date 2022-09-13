"""
Serializers
"""

from rest_framework  import serializers
from geotmlnh.models import facedata, fevents, refdata, lyrevents

class CFaceSerial(serializers.ModelSerializer):
    class Meta:
        model  = facedata
        fields = ("post_id", "description", "message", "datahora",
                  "page_ref", "type")


class RefDataSerial(serializers.ModelSerializer):
    fb = CFaceSerial(many=True, read_only=True)
    
    class Meta:
        model = refdata
        fields = ("fid", "postid", "is_fire", "fb")

class LyrEvents(serializers.ModelSerializer):
    class Meta:
        model = lyrevents
        fields = ("fid", "name", "geosrv", "style")


class FireEventsSerial(serializers.ModelSerializer):
    contrib = RefDataSerial(many=True, read_only=True)
    lyr     = LyrEvents(many=True, read_only=True)
    
    class Meta:
        model = fevents
        fields = ("fid", "event", "tstart", "tend", "contrib", "lyr")

