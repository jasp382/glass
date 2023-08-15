from django.contrib.gis.db import models

# Create your models here.

class MeteoSource(models.Model):
    """
    Meteorological Source
    """

    slug  = models.CharField(max_length=15)
    name  = models.CharField(max_length=20)
    description = models.CharField(max_length=30)
    url = models.CharField(max_length=100)
    token = models.CharField(max_length=100, null=True, blank=True)

class MeteoVariables(models.Model):
    """
    Meteorological Variables
    """

    slug  = models.CharField(max_length=50)
    name  = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    unit = models.CharField(max_length=15)
    source = models.ForeignKey(
        MeteoSource, on_delete=models.CASCADE, db_index=True,
        db_column="source"
    )

class MeteoStation(models.Model):
    """
    Meteorological Stations
    """

    idapi = models.IntegerField()
    name = models.CharField(max_length=100)
    geom = models.PointField(srid=3763)


class MeteoObservation(models.Model):
    """
    Meteorological Observations
    """

    date    = models.DateTimeField()
    station = models.ForeignKey(
        MeteoStation, on_delete=models.CASCADE, db_index=True,
        db_column="station"
    )

class MeteoObservationValues(models.Model):
    """
    Meteorological Observation Values
    """

    varid = models.ForeignKey(
        MeteoVariables, on_delete=models.CASCADE, db_index=True,
        db_column='varid'
    )
    obsid = models.ForeignKey(
        MeteoObservation, on_delete=models.CASCADE, db_index=True,
        db_column="obsid", related_name="obsid"
    )
    value = models.DecimalField(max_digits=15, decimal_places=5)


class MeteoForecast(models.Model):
    """
    Meteorological Forecast
    """

    date = models.DateTimeField()
    geom =  models.PointField(srid=3763, blank=True, null=True)


class MeteoForecastValues(models.Model):
    """
    Meteorological Forecast Values
    """

    varid = models.ForeignKey(
        MeteoVariables, on_delete=models.CASCADE, db_index=True,
        db_column='varid'
    )
    forecid = models.ForeignKey(
        MeteoForecast, on_delete=models.CASCADE, db_index=True,
        db_column="forecid", related_name="forecid"
    )
    value = models.DecimalField(max_digits=15, decimal_places=5)
