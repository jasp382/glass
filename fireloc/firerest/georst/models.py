from django.contrib.gis.db import models

from georef.models import RefGrid

# Create your models here.


class RasterTypes(models.Model):
    """
    Datasets Types
    """

    slug = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)


class RasterDatasets(models.Model):
    """
    Raster Datasets
    """

    slug = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    refyear = models.IntegerField(null=True, blank=True)
    refprod = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=75)

    idtype = models.ForeignKey(
        RasterTypes, on_delete=models.CASCADE, db_index=True,
        db_column="idtype"
    )


class RasterLayers(models.Model):
    """
    Raster Layers
    """

    layer = models.CharField(max_length=15, unique=True)
    cellsizex = models.IntegerField(null=True, blank=True)
    cellsizey = models.IntegerField(null=True, blank=True)
    method = models.CharField(max_length=500)

    level = models.IntegerField(null=True, blank=True)

    refgrid = models.ForeignKey(
        RefGrid, on_delete=models.CASCADE, db_index=True,
        db_column="refgrid", null=True, blank=True
    )

    idrst = models.ForeignKey(
        RasterDatasets, on_delete=models.CASCADE, db_index=True,
        db_column="idrst"
    )
