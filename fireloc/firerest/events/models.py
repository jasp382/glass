from django.contrib.gis.db import models
from georef.models import Freguesias, Concelhos, Places

# Create your models here.

class Years(models.Model):
    year = models.IntegerField(unique=True)


class RealFireEvents(models.Model):
    """
    Store real fire events information
    """

    codsgif = models.CharField(max_length=50,null=True, blank=True)
    codncco = models.CharField(max_length=50,null=True, blank=True)
    tipo    = models.CharField(max_length=50,null=True, blank=True)
    causa   = models.CharField(max_length=50,null=True, blank=True)
    name    = models.CharField(max_length=100, null=True, blank=True)
    start   = models.DateTimeField()
    end     = models.DateTimeField()
    geom    = models.MultiPolygonField(srid=3763)
    freg    = models.ManyToManyField(Freguesias)
    mun     = models.ManyToManyField(Concelhos)
    nearplace = models.ForeignKey(
        Places, on_delete=models.CASCADE, db_index=True,
        db_column="nearplace", null=True, blank=True
    )
    step = models.IntegerField(default=0)

    fregid = models.ForeignKey(
        Freguesias, on_delete=models.CASCADE, db_index=True,
        db_column="fregid", null=True, blank=True,
        related_name='onefreg'
    )


class BurnAreas(models.Model):
    """
    Store data about burned area
    """

    geom     = models.PolygonField(srid=3763)
    refstart = models.DateField()
    refend   = models.DateField()

    years = models.ManyToManyField(Years)

