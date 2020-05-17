from rest_framework import serializers

"""
Serializer for Datasets submited by the user
"""

from weapi.models import UploadData, UploadCols
class ListDatasetCols(serializers.ModelSerializer):
    class Meta:
        model = UploadCols
        fields = ("fid", "name_col", "idx_col", "ctx_col")

class ListDatasets(serializers.ModelSerializer):
    cols = ListDatasetCols(many=True, read_only=True)
    
    class Meta:
        model = UploadData
        fields = ("fid", "filename", "cols")

"""
Serializer for Years
"""
from weapi.models import Years
class ListYears(serializers.ModelSerializer):
    class Meta:
        model = Years
        fields = ("fid", "year")