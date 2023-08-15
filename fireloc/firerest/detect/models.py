from django.contrib.gis.db import models

from georef.models import Places, Freguesias
from contrib.models import VolunteersContributions

# Create your models here.

class FirelocApproach(models.Model):
    """
    Fire location Assessment approachs
    """

    slug = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)


class FirelocAssessment(models.Model):
    """
    Fire Location Assessment
    """

    startime = models.DateTimeField(null=True, blank=True)
    endtime  = models.DateTimeField(null=True, blank=True)
    ctbstart = models.DateTimeField()
    ctbend   = models.DateTimeField()

    aprch = models.ForeignKey(
        FirelocApproach, on_delete=models.CASCADE, db_index=True,
        db_column="aprch"
    )

    nearplace = models.ForeignKey(
        Places, on_delete=models.CASCADE, db_index=True,
        db_column="nearplace", null=True, blank=True
    )

    fregid = models.ForeignKey(
        Freguesias, on_delete=models.CASCADE, db_index=True,
        db_column="fregid", null=True, blank=True
    )

    ctbs = models.ManyToManyField(VolunteersContributions, related_name='ctbs')

    step = models.IntegerField(default=0)

    extent = models.PolygonField(srid=3763, blank=True, null=True)
    geom   = models.PolygonField(srid=3763, blank=True, null=True)

    prid = models.CharField(max_length=20)


class FirelocAttr(models.Model):
    """
    Fire location Assessment Attributes
    """

    slug  = models.CharField(max_length=10)
    name  = models.CharField(max_length=50)
    dtype = models.CharField(max_length=15)


class FirelocAttrValue(models.Model):
    """
    Fire location Assessment Attributes values
    """

    fattr = models.ForeignKey(
        FirelocAttr, on_delete=models.CASCADE, db_index=True,
        db_column='fattr', related_name="fattr"
    )

    floc = models.ForeignKey(
        FirelocAssessment, on_delete=models.CASCADE, db_index=True,
        db_column="floc", related_name="attr"
    )

    value = models.CharField(max_length=250, null=True)
    pointgeom = models.PointField(srid=3763, blank=True, null=True)
    polygeom  = models.PolygonField(srid=3763, null=True, blank=True)


class PhotoClassification(models.Model):
    """
    Photo classification data
    """

    isfire  = models.BooleanField()
    issmoke = models.BooleanField()

    pic = models.CharField(max_length=200, null=True, blank=True)

    ctb = models.ForeignKey(
        VolunteersContributions, on_delete=models.CASCADE,
        db_index=True, db_column='ctb'
    )


class PhotoClassAttr(models.Model):
    """
    Photo classification attribute
    """

    slug  = models.CharField(max_length=10)
    name  = models.CharField(max_length=50)
    dtype = models.CharField(max_length=15)


class PhotoClassAttrValue(models.Model):
    """
    Photo classification attributes values
    """
    value = models.CharField(max_length=250)
    pcattr = models.ForeignKey(
        PhotoClassAttr, on_delete=models.CASCADE, db_index=True,
        db_column="pcattr", related_name='aattr'
    )

    photocls = models.ForeignKey(
        PhotoClassification, on_delete=models.CASCADE, db_index=True,
        db_column="photocls", related_name="clsattr"
    )
    

    #value = models.CharField(max_length=15)


class SunData(models.Model):
    """
    Table to store Geocentric sun right ascension and 
    Geocentric sun declination
    """

    datehour    = models.DateTimeField()
    ascension   = models.DecimalField(max_digits=15, decimal_places=6)
    declination = models.DecimalField(max_digits=15, decimal_places=6)


class FireSimProcedures(models.Model):
    """
    Fire Simulation Procedures
    """

    stepone = models.IntegerField()
    steptwo = models.IntegerField()
    stepthree = models.IntegerField()
    stepfour  = models.IntegerField()
    prcdid    = models.CharField(max_length=20)


class FireSimulation(models.Model):
    """
    Fire Simulation 
    """

    pid = models.ForeignKey(
        FireSimProcedures, on_delete=models.CASCADE,
        db_index=True, db_column="pid",
        related_name='fsimp'
    )

    floc = models.ForeignKey(
        FirelocAssessment, on_delete=models.CASCADE,
        db_index=True, db_column="floc"
    )

