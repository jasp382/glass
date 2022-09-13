from django.contrib.gis.db import models

"""
Data storage for DSN Map Search Web Service
"""

class rqsts(models.Model):
    """
    Record Requests for utilization of DSN Web Service
    """
    
    fid           = models.CharField(max_length=10, primary_key=True)
    search_keys   = models.CharField(max_length=50, blank=True, null=True)
    date          = models.DateField()
    start_time    = models.TimeField()
    end_time      = models.TimeField(blank=True, null=True)
    status        = models.CharField(max_length=50, blank=True, null=True)
    error         = models.CharField(max_length=10000, blank=True, null=True)
    isfb          = models.BooleanField()
    istw          = models.BooleanField()
    isyoutb       = models.BooleanField()
    isflickr      = models.BooleanField()
    cntfb         = models.IntegerField()
    cnttw         = models.IntegerField()
    cntyoutb      = models.IntegerField()
    cntflickr     = models.IntegerField()
    user_id       = models.IntegerField()


class lyr(models.Model):
    fid = models.CharField(max_length=13, primary_key=True)
    rqst = models.ForeignKey(
        'rqsts', on_delete=models.CASCADE, db_index=True,
        db_column='rqst', related_name='lyr_rqsts'
    )
    slug = models.CharField(max_length=5)
    name = models.CharField(max_length=20)
    style = models.CharField(max_length=20)
    url   = models.CharField(max_length=250)
    dw_url = models.CharField(max_length=250)


class searchgeom(models.Model):
    """
    Search Geometries
    """
    
    fid = models.CharField(max_length=20, primary_key=True)
    lyr_id = models.ForeignKey(
        'lyr', on_delete=models.CASCADE, db_index=True,
        db_column='lyr_id', related_name='lyr_feat'
    )
    geom = models.PolygonField(srid=3857, blank=True, null=True)


class twitter(models.Model):
    id      = models.CharField(max_length=20, primary_key=True)
    fid     = models.BigIntegerField()
    lyr_id  = models.ForeignKey(
        'lyr', on_delete=models.CASCADE, db_index=True,
        db_column='lyr_id', related_name='lyr_tw'
    )
    text    = models.CharField(max_length=255, blank=True, null=True)
    user    = models.CharField(max_length=255, blank=True, null=True)
    url     = models.CharField(max_length=255, blank=True, null=True)
    geom    = models.PointField(srid=3857)


class facebook(models.Model):
    id          = models.CharField(max_length=20, primary_key=True)
    fid         = models.BigIntegerField()
    lyr_id     = models.ForeignKey(
        'lyr', on_delete=models.CASCADE, db_index=True,
        db_column='lyr_id', related_name='lyr_fb'
    )
    fb_type     = models.CharField(max_length=20)
    url         = models.CharField(max_length=100)
    name_1      = models.CharField(max_length=100)
    about       = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True, null=True)
    fan_count   = models.IntegerField(blank=True, null=True)
    checkins    = models.IntegerField(blank=True, null=True)
    geom        = models.PointField(srid=3857)
    id_2        = models.BigIntegerField(blank=True, null=True)
    id_3        = models.BigIntegerField(blank=True, null=True)
    id_4        = models.BigIntegerField(blank=True, null=True)
    id_5        = models.BigIntegerField(blank=True, null=True)
    name_2      = models.CharField(max_length=100, blank=True, null=True)
    name_3      = models.CharField(max_length=100, blank=True, null=True)
    name_4      = models.CharField(max_length=100, blank=True, null=True)
    name_5      = models.CharField(max_length=100, blank=True, null=True)


class flickr(models.Model):
    id         = models.CharField(max_length=20, primary_key=True)
    fid        = models.BigIntegerField()
    lyr_id    = models.ForeignKey(
        'lyr', on_delete=models.CASCADE, db_index=True,
        db_column='lyr_id', related_name='lyr_flckr'
    )
    owner       = models.CharField(max_length=255, blank=True, null=True)
    place_id    = models.CharField(max_length=255, blank=True, null=True)
    title       = models.CharField(max_length=255, blank=True, null=True)
    name        = models.CharField(max_length=255, blank=True, null=True)
    datetaken   = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=10000, blank=True, null=True)
    dateupload  = models.CharField(max_length=255, blank=True, null=True)
    url         = models.CharField(max_length=255, blank=True, null=True)
    geom        = models.PointField(srid=3857)

