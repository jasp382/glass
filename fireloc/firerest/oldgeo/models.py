from django.contrib.gis.db import models

# Create your models here.

"""
Old Models
"""

class DatasetTypes(models.Model):
    """
    Dataset Types
    """

    dtid = models.IntegerField(primary_key=True)
    slug = models.CharField(max_length=20)


class Datasets(models.Model):
    """
    Datasets List
    """

    did = models.AutoField(primary_key=True)
    slug = models.CharField(max_length=20)
    descricao = models.CharField(max_length=250)
    ano_ref = models.IntegerField(blank=True, null=True)
    ano_prod = models.IntegerField(blank=True, null=True)
    fonte    = models.CharField(max_length=250)
    method   = models.CharField(max_length=100, blank=True, null=True)
    cellsize = models.IntegerField()
    storage_type = models.CharField(max_length=50, blank=True, null=True)
    storage = models.CharField(max_length=50)
    dtid = models.ForeignKey(
        "DatasetTypes", on_delete=models.CASCADE,
        db_column='dtid', related_name='dtsets'
    )
    events = models.ManyToManyField('ExtremeEvents', related_name='datasets', blank=True)


class ExtremeEvents(models.Model):
    """
    Extreme Events List
    """

    eid = models.AutoField(primary_key=True)
    slug = models.CharField(max_length=20)
    description = models.CharField(max_length=250)


class DataExtracts(models.Model):
    """
    List Dataset Extracts
    """

    fid   = models.AutoField(primary_key=True)
    token = models.CharField(max_length=50)
    dataset = models.CharField(max_length=50)
    storage = models.CharField(max_length=3)
    geom    = models.PolygonField(srid=3763)


"""
OSM Related
"""

class OsmCountries(models.Model):
    """
    Countries OSM
    """

    fid       = models.IntegerField(primary_key=True)
    continent = models.CharField(max_length=50)
    country   = models.CharField(max_length=100)
    geom      = models.MultiPolygonField(srid=4326)