from django.contrib.gis.db import models

from layers.models import Layers

# Create your models here.


class Geodata(models.Model):
    """
    Geospatial data of each layer
    """

    code = models.CharField(max_length=15)
    name = models.CharField(max_length=100)

    geom = models.PolygonField(srid=3763, null=True, blank=True)
    layerid = models.ForeignKey(
        Layers, on_delete=models.CASCADE, db_index=True,
        db_column="layerid"
    )
