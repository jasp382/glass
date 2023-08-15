from django.contrib.gis.db import models

# Create your models here.


class VectorCat(models.Model):
    """
    Vector Datasets Categories
    """

    slug = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)


class VectorDatasets(models.Model):
    """
    Vectorial Datasets
    """

    POINT           = 'POINT'
    LINESTRING      = 'LINESTRING'
    POLYGON         = 'POLYGON'
    MULTIPOINT      = 'MULTIPOINT'
    MULTILINESTRING = 'MULTILINESTRING'
    MULTIPOLYGON    = 'MULTIPOLYGON'

    GTYPES_CHOICES = [
        (POINT, 'Point'),
        (LINESTRING, 'LineString'),
        (POLYGON, 'Polygon'),
        (MULTIPOINT, 'MultiPoint'),
        (MULTILINESTRING, 'MultiLineString'),
        (MULTIPOLYGON, 'MultiPolygon')
    ]

    slug = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    refyear = models.IntegerField(null=True, blank=True)
    refprod = models.IntegerField(null=True, blank=True)
    source = models.CharField(max_length=75)
    gtype = models.CharField(
        max_length=20, choices=GTYPES_CHOICES,
        default=POLYGON
    )

    catid = models.ForeignKey(
        VectorCat, on_delete=models.CASCADE,
        db_index=True, db_column='catid'
    )


class VectorLevels(models.Model):
    """
    Generalization Levels
    """

    slug = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250)
    level = models.IntegerField()

    dsetid = models.ForeignKey(
        VectorDatasets, on_delete=models.CASCADE,
        db_index=True, db_column='dsetid',
        related_name="dsetlevel"
    )

