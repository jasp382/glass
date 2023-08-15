from django.contrib.gis.db import models
from django.contrib.auth.models import Group

from authapi.models import Organizations
from events.models  import RealFireEvents
from detect.models  import FirelocAssessment
from contrib.models import VolunteersContributions

# Create your models here.

class MapFireAss(models.Model):
    """
    Layers to show the results of the fire loc
    assessment
    """

    slug = models.CharField(max_length=15, unique=True)
    design = models.CharField(max_length=100)
    work   = models.CharField(max_length=20)
    store  = models.CharField(max_length=20)
    glyr   = models.CharField(max_length=40)
    style  = models.CharField(max_length=20)

    datehour = models.DateTimeField()

    flocid = models.ForeignKey(
        FirelocAssessment, on_delete=models.CASCADE, db_index=True,
        db_column="flocid", related_name='floclyr'
    )


class FireMapLeg(models.Model):
    """
    Fireloc Layers legend
    """

    cat    = models.CharField(max_length=100, null=True, blank=True)
    minval = models.CharField(max_length=20, null=True, blank=True)
    maxval = models.CharField(max_length=20, null=True, blank=True)
    color  = models.CharField(max_length=8)
    label  = models.CharField(max_length=50)
    order  = models.IntegerField()
    lyrid  = models.ForeignKey(
        MapFireAss, on_delete=models.CASCADE, db_index=True,
        db_column="lyrid", related_name='flyrleg'
    )


class EventsLayers(models.Model):
    """
    Layers to show real fires events
    """

    slug = models.CharField(max_length=15, unique=True)
    design = models.CharField(max_length=100)
    work   = models.CharField(max_length=20)
    store  = models.CharField(max_length=20)
    glyr   = models.CharField(max_length=40)
    style  = models.CharField(max_length=20)

    fireid = models.ForeignKey(
        RealFireEvents, on_delete=models.CASCADE, db_index=True,
        db_column="fireid", related_name='firelyr'
    )

class EventsMapLeg(models.Model):
    """
    Events Layers legend
    """

    cat    = models.CharField(max_length=100, null=True, blank=True)
    minval = models.CharField(max_length=20, null=True, blank=True)
    maxval = models.CharField(max_length=20, null=True, blank=True)
    color  = models.CharField(max_length=8)
    label  = models.CharField(max_length=50)
    order  = models.IntegerField()
    lyrid  = models.ForeignKey(
        EventsLayers, on_delete=models.CASCADE, db_index=True,
        db_column="lyrid", related_name='fireleg'
    )


class MapLayers(models.Model):
    """
    GeoPortal Map Layers
    """

    slug        = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=250)
    workspace   = models.CharField(max_length=20, null=True, blank=True)
    store       = models.CharField(max_length=20, null=True, blank=True)
    gsrvlyr     = models.CharField(max_length=40, null=True, blank=True)
    style       = models.CharField(max_length=20, null=True, blank=True)

    level = models.IntegerField()

    rootid = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name="childs"
    )

    usgroup = models.ManyToManyField(Group, related_name='maplayers')
    orgs    = models.ManyToManyField(Organizations)


class MapLayerAttr(models.Model):
    """
    GeoPortal Map Layers Attributes
    """

    slug = models.CharField(max_length=15)
    label = models.CharField(max_length=20)
    layerid = models.ForeignKey(
        MapLayers, on_delete=models.CASCADE, db_index=True,
        db_column="layerid", related_name='lyrattr'
    )

    usgroup = models.ManyToManyField(Group)
    orgs    = models.ManyToManyField(Organizations)


class MapsLegend(models.Model):
    """
    Layers legend
    """

    cat = models.CharField(max_length=100, null=True, blank=True)
    minval = models.CharField(max_length=20, null=True, blank=True)
    maxval = models.CharField(max_length=20, null=True, blank=True)
    color  = models.CharField(max_length=8)
    label  = models.CharField(max_length=50)
    order  = models.IntegerField()
    layerid = models.ForeignKey(
        MapLayers, on_delete=models.CASCADE, db_index=True,
        db_column="layerid", related_name='lyrleg'
    )


class GeoCharts(models.Model):
    """
    Geographic Charts
    """

    BAR = "BAR"
    LINE = "LINE"
    PIE  = "PIE"
    SCATTER = "SCATTER"

    CHARTS_CHOICES = [
        (BAR, "Bar Chart"),
        (LINE, "Line Chart"),
        (PIE, "Pie Chart"),
        (SCATTER, "Scatter Plot")
    ]

    slug        = models.CharField(max_length=10)
    designation = models.CharField(max_length=30)
    description = models.CharField(max_length=250)
    chartype    = models.CharField(
        max_length=8, choices=CHARTS_CHOICES, default=BAR
    )

    usgroup = models.ManyToManyField(Group)
    orgs    = models.ManyToManyField(Organizations)


class ChartsSeries(models.Model):
    """
    Store Data Series of Charts
    """

    slug = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    chartid = models.ForeignKey(
        GeoCharts, on_delete=models.CASCADE, db_index=True,
        db_column="chartid", related_name='series'
    )


class ChartsData(models.Model):
    """
    Store charts data
    """

    xvalue = models.DecimalField(max_digits=10, decimal_places=3)
    yvalue = models.DecimalField(max_digits=10, decimal_places=3)
    sid    = models.ForeignKey(
        ChartsSeries, on_delete=models.CASCADE, db_index=True,
        db_column="sid"
    )

class ClusterLayers(models.Model):
    """
    Cluster Layers
    """

    slug        = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=50)
    workspace   = models.CharField(max_length=20)
    store       = models.CharField(max_length=20)
    gsrvlyr     = models.CharField(max_length=40)

    level       = models.IntegerField()

    eps         = models.IntegerField()
    minpts      = models.IntegerField()
    maxzoom     = models.IntegerField()
    minzoom     = models.IntegerField()

    #usgroup = models.ManyToManyField(Group)
    #orgs    = models.ManyToManyField(Organizations)


class PermLayers(models.Model):
    """
    Permanent Layers
    """

    slug = models.CharField(max_length=15, unique=True)
    designation = models.CharField(max_length=50)
    workspace   = models.CharField(max_length=20)
    store       = models.CharField(max_length=20)
    gsrvlyr     = models.CharField(max_length=40)

    query = models.CharField(max_length=50000)


class SingleCtbLayers(models.Model):
    """
    Single Contribution Map Layers 
    """

    slug  = models.CharField(max_length=15, unique=True)
    desig = models.CharField(max_length=50)
    work  = models.CharField(max_length=20)
    store = models.CharField(max_length=20)
    layer = models.CharField(max_length=40)
    style = models.CharField(max_length=20, null=True, blank=True)

    wms = models.BooleanField()

    ctb = models.ForeignKey(
        VolunteersContributions, on_delete=models.CASCADE,
        db_index=True, db_column="ctb"
    )

