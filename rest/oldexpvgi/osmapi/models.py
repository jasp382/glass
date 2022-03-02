from django.contrib.gis.db import models

# Create your models here.
class OsmCountries(models.Model):
    """
    Countries OSM
    """

    fid       = models.IntegerField(primary_key=True)
    continent = models.CharField(max_length=50)
    country   = models.CharField(max_length=100)
    geom      = models.MultiPolygonField(srid=4326)

