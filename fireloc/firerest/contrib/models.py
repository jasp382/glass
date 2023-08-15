from django.contrib.gis.db import models
from django.conf import settings

from georef.models import Places, Freguesias

# Create your models her

class VolunteersContributions(models.Model):
    """
    Contributions data
    """

    fid = models.AutoField(primary_key=True)
    pic = models.CharField(max_length=200, null=True, blank=True)
    respic = models.CharField(max_length=200, null=True, blank=True)
    datehour = models.DateTimeField()
    usergeom = models.PointField(srid=3763, null=True, blank=True)
    ugazimute = models.IntegerField(null=True, blank=True)
    dist = models.CharField(max_length=30,null=True, blank=True)
    direction = models.IntegerField()
    dsun = models.IntegerField(null=True, blank=True)
    directbf = models.IntegerField(null=True, blank=True)
    orie = models.IntegerField(null=True, blank=True)
    beta = models.IntegerField(null=True, blank=True)
    gama = models.IntegerField(null=True, blank=True)
    txt  = models.CharField(max_length=250, null=True, blank=True)
    cuser = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, db_index=True,
        db_column='cuser', related_name='cuser'
    )
    pnt_name = models.CharField(max_length=100, null=True, blank=True)
    fire_name = models.CharField(max_length=100, null=True, blank=True)
    
    geomc = models.PointField(srid=3763, null=True, blank=True)
    geombfc = models.PointField(srid=3763, null=True, blank=True)
    gazimute = models.IntegerField(null=True, blank=True)
    gbfazimute = models.IntegerField(null=True, blank=True)
    place = models.ForeignKey(
        Places, on_delete=models.CASCADE, db_index=True,
        db_column='place', null=True, blank=True
    )
    fregid = models.ForeignKey(
        Freguesias, on_delete=models.CASCADE, db_index=True,
        db_column="fregid", null=True, blank=True
    )

    strips = models.IntegerField(default=0)

    photostatus = models.IntegerField(default=0)

    stripgeom = models.PolygonField(srid=3763, null=True, blank=True)
    stripext  = models.PolygonField(srid=3763, blank=True, null=True)


class VolunteersPositions(models.Model):
    """
    Volunteers Contributions positions
    """

    pid  = models.IntegerField()
    geom = models.PointField(srid=3763)
    azimute = models.IntegerField(null=True, blank=True)
    cid = models.ForeignKey(
        VolunteersContributions, on_delete=models.CASCADE,
        db_index=True, db_column="cid", related_name='geom'
    )


class VolunteersPositionsBackFront(models.Model):
    """
    Volunteers Contribuitions positions after steps back/front
    """

    pid  = models.IntegerField()
    geom = models.PointField(srid=3763)
    azimute = models.IntegerField(null=True, blank=True)
    cid = models.ForeignKey(
        VolunteersContributions, on_delete=models.CASCADE,
        db_index=True, db_column="cid", related_name="geombf"
    )

