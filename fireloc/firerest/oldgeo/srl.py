"""
Serializarers for this django app
"""

from rest_framework import serializers

"""
Datasets Serializer
"""

from oldgeo.models import Datasets, DatasetTypes


class DatasetsSerial(serializers.ModelSerializer):
    class Meta:
        model = Datasets
        fields = (
            'did', 'slug', 'descricao', 'ano_ref',
            'ano_prod', 'fonte', 'method',
            'cellsize', 'storage_type', 'storage'
        )
    
    def create(self, data):
        """
        Add new dataset
        """

        return Datasets.objects.create(
            slug=data.get("slug"), descricao=data.get("descricao"),
            ano_ref=data.get("ano_ref", None),
            ano_prod=data.get("ano_prod", None),
            fonte=data.get("fonte"),
            method=data.get("method", None),
            cellsize=data.get("cellsize"),
            storage_type=data.get("storage_type", "gpkg"),
            storage=data.get("storage")
        )

    def update(self, i, data):
        """
        Update and return an existing Dataset Instance
        """

        i.slug = data.get('slug', i.slug)
        i.descricao = data.get('descricao', i.descricao)
        i.ano_ref   = data.get('ano_ref', i.ano_ref)
        i.ano_prod  = data.get('ano_prod', i.ano_prod)
        i.fonte     = data.get('fonte', i.fonte)
        i.method    = data.get('method', i.method)
        i.cellsize  = data.get('cellsize', i.cellsize)
        i.storage_type  = data.get('rst_gpkg', i.rst_gpkg)
        i.storage  = data.get('shp_gpkg', i.shp_gpkg)

        i.save()

        return i


class DataTypesSrl(serializers.ModelSerializer):
    dtsets = DatasetsSerial(many=True, read_only=True)

    class Meta:
        model = DatasetTypes
        fields = ('dtid', 'slug', 'dtsets')


from oldgeo.models import ExtremeEvents
    

class EventsSrl(serializers.ModelSerializer):
    datasets = DatasetsSerial(many=True, read_only=True)

    class Meta:
        model = ExtremeEvents
        fields = ("eid", "slug", "description", "datasets")


from oldgeo.models import DataExtracts

class DataExtractsSrl(serializers.ModelSerializer):
    class Meta:
        model = DataExtracts
        fields = ("fid", "token", "dataset", "storage", "geom")
    
    def create(self, vd):
        from django.contrib.gis.geos import GEOSGeometry

        return DataExtracts.objects.create(
            geom=GEOSGeometry(vd["geom"], srid=3763),
            dataset=vd["dataset"], token=vd["token"],
            storage=vd["storage"]
        )

