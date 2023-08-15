from django.contrib.gis.db import models

# Create your models here.

from georef.models import RefGrid


class SentinelTiles(models.Model):
    """
    Sentinel Tiles
    """

    slugid = models.CharField(max_length=10, unique=True)
    geom   = models.PolygonField(srid=3763)

    reftile = models.ManyToManyField(RefGrid)


class SentinelImages(models.Model):
    """
    Sentinel Images
    """

    title = models.CharField(max_length=1000)
    link  = models.CharField(max_length=1000)
    summary  = models.CharField(max_length=1000)
    ondemand = models.CharField(max_length=1000)
    beginposition  = models.DateTimeField()
    endposition = models.DateTimeField()
    ingestiondate = models.DateTimeField()
    generationdate = models.DateTimeField()
    orbitnumber = models.IntegerField()
    relativeorbitnumber  = models.IntegerField()
    vegetationpercentage = models.DecimalField(max_digits=8, decimal_places=3)
    notvegetatedpercentage = models.DecimalField(max_digits=8, decimal_places=3)
    waterpercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    unclassifiedpercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    mediumprobacloudspercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    highprobacloudspercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    snowicepercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    cloudcoverpercentage  = models.DecimalField(max_digits=8, decimal_places=3)
    illuminationazimuthangle  = models.DecimalField(
        max_digits=8, decimal_places=3,
        null=True, blank=True
    )
    illuminationzenithangle  = models.DecimalField(
        max_digits=8, decimal_places=3,
        null=True, blank=True
    )
    level1cpdiidentifier  = models.CharField(max_length=1000)
    format  = models.CharField(max_length=1000)
    processingbaseline  = models.CharField(max_length=1000)
    platformname  = models.CharField(max_length=1000)
    filename  = models.CharField(max_length=1000)
    instrumentname  = models.CharField(max_length=1000)
    instrumentshortname  = models.CharField(max_length=1000)
    size  = models.CharField(max_length=1000)
    s2datatakeid  = models.CharField(max_length=1000)
    producttype  = models.CharField(max_length=1000)
    platformidentifier  = models.CharField(max_length=1000)
    orbitdirection  = models.CharField(max_length=1000)
    platformserialidentifier  = models.CharField(max_length=1000, null=True, blank=True)
    processinglevel  = models.CharField(max_length=1000)
    identifier  = models.CharField(max_length=1000)
    datastripidentifier  = models.CharField(max_length=1000)
    granuleidentifier  = models.CharField(max_length=1000)
    uuid  = models.CharField(max_length=1000, unique=True)
    geometry = models.MultiPolygonField(srid=3763)

    reftile = models.ForeignKey(
        RefGrid, on_delete=models.CASCADE, db_index=True,
        db_column='reftile', null=True, blank=True
    )
    tileid = models.ForeignKey(
        SentinelTiles, on_delete=models.CASCADE, db_index=True,
        db_column="tileid"
    )

    isdownload = models.BooleanField()

