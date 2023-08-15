from django.db import models

from django.contrib.auth.models import User

# Create your models here.


class Logs(models.Model):
    """
    Table to store logs data
    """

    fid      = models.AutoField(primary_key=True)
    url      = models.CharField(max_length=100)
    service  = models.CharField(max_length=50)
    http     = models.IntegerField()
    code     = models.CharField(max_length=5)
    message  = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data     = models.CharField(max_length=5000, null=True, blank=True)
    method   = models.CharField(max_length=10)
    cuser    = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='luser',
        null=True, blank=True
    )


class LogsToken(models.Model):
    """
    Record all interactions with all endpoints
    """

    fid      = models.AutoField(primary_key=True)
    url      = models.CharField(max_length=100)
    service  = models.CharField(max_length=50)
    http     = models.IntegerField()
    code     = models.CharField(max_length=10)
    message  = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data     = models.CharField(max_length=5000, null=True, blank=True)
    method   = models.CharField(max_length=10)
    cuser    = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="cuser", related_name="ltuser",
        null=True, blank=True
    )


class LogsAuth(models.Model):
    """
    Record all interactions with all endpoints
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=10)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="cuser", related_name="lauser",
        null=True, blank=True
    )


class LogsGeoRef(models.Model):
    """
    Record all interactions with all endpoints
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=10)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="cuser", related_name="gruser",
        null=True, blank=True
    )


class LogsGeoRst(models.Model):
    """
    Record all interactions with all endpoints
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=10)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="cuser", related_name="grstuser",
        null=True, blank=True
    )


class LogsContrib(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='cntuser',
        null=True, blank=True
    )


class LogsEvents(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='evuser',
        null=True, blank=True
    )


class LogsSdi(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='sdiuser',
        null=True, blank=True
    )


class LogsGeovis(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='geovisuser',
        null=True, blank=True
    )


class LogsFiredetect(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='fdetectuser',
        null=True, blank=True
    )


class LogsGeosat(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='geosatuser',
        null=True, blank=True
    )

class LogsMeteo(models.Model):
    """
    Table to store logs data
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=5)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='cuser', related_name='meteouser',
        null=True, blank=True
    )


class LogsGeoVec(models.Model):
    """
    Record all interactions with all endpoints
    """

    fid = models.AutoField(primary_key=True)
    url = models.CharField(max_length=100)
    service = models.CharField(max_length=50)
    http = models.IntegerField()
    code = models.CharField(max_length=10)
    message = models.CharField(max_length=1000)
    datehour = models.DateTimeField()
    data = models.CharField(max_length=5000, null=True, blank=True)
    method = models.CharField(max_length=10)
    cuser = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="cuser", related_name="gvecuser",
        null=True, blank=True
    )

