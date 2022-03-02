from django.contrib.gis.db import models

# Create your models here.

class rqsts(models.Model):
    """
    Record Requests for utilization of OSM2LULC Web Service
    """
    
    fid          = models.CharField(max_length=10, primary_key=True)
    nomenclature = models.CharField(max_length=50, blank=True, null=True)
    date         = models.DateField(blank=True, null=True)
    start_time   = models.TimeField(blank=True, null=True)
    end_time     = models.TimeField(blank=True, null=True)
    status       = models.CharField(max_length=50, blank=True, null=True)
    error        = models.CharField(max_length=10000, blank=True, null=True)
    filesize     = models.DecimalField(
        max_digits=10, decimal_places=3, blank=True, null=True)
    user_id      = models.IntegerField()


class lyr(models.Model):
    """
    List of Layers Related with OSM2LULC Request
    """
    
    fid = models.CharField(max_length=13, primary_key=True)
    rqst = models.ForeignKey(
        'rqsts', on_delete=models.CASCADE, db_index=True,
        db_column='rqst', related_name='lyr_rqsts'
    )
    slug = models.CharField(max_length=5)
    name = models.CharField(max_length=20)
    lyrt = models.CharField(max_length=20)
    lname = models.CharField(max_length=20, blank=True, null=True)
    style = models.CharField(max_length=20)
    url   = models.CharField(max_length=250)
    dw_url = models.CharField(max_length=250)


class lyr_feat(models.Model):
    """
    Layers Features Collection
    """
    
    fid = models.CharField(max_length=20, primary_key=True)
    lyr = models.ForeignKey(
        'lyr', on_delete=models.CASCADE, db_index=True,
        db_column='rqst', related_name='lyr_feat'
    )
    geom = models.PolygonField(srid=3857, blank=True, null=True)

