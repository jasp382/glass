"""
Models Serializers
"""

from rest_framework import serializers

from layers.models import Layers

from api.settings import GEOSERVER_CON

class LayersSrl(serializers.ModelSerializer):
    islayer = serializers.SerializerMethodField('is_layer')
    classes = serializers.SerializerMethodField('get_classes')

    class Meta:
        model = Layers
        fields = [
            "id", "alias", "design", "style", "islayer",
            "classes"
        ]
    
    def is_layer(self, obj):
        from pwtools.gsrv.lyrs import lst_lyr

        ws = GEOSERVER_CON["WORKSPACE"]

        ln = f"{ws}:layer_{obj.id}"

        lyrs = lst_lyr()

        return False if ln not in lyrs else True
    
    def get_classes(self, obj):
        from gserver.tools import q_to_obj

        d = q_to_obj("api_db", (
            "SELECT code "
            "FROM geoms_geodata "
            f"WHERE layerid = {str(obj.id)} "
            "GROUP BY code"
        ))

        return d["code"].tolist()

