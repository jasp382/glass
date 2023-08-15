from django.contrib.gis.db import models

# Create your models here.


class ExtentGeometry(models.Model):
    """
    Geometry to define maps extent
    """

    geom = models.PolygonField(srid=3763)


class RefGrid(models.Model):
    """
    Reference GRID Table
    """

    gid    = models.AutoField(primary_key=True)
    cellid = models.IntegerField()
    geom   = models.PolygonField(srid=3763)


class Nutsii(models.Model):
    """
    NUT's II Model
    """

    fid  = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50, unique=True)
    geom = models.MultiPolygonField(srid=3763)


class Nutsiii(models.Model):
    """
    NUT III Model
    """

    fid  = models.AutoField(primary_key=True)
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=50, unique=True)
    geom = models.MultiPolygonField(srid=3763)
    nutii = models.ForeignKey(
        Nutsii, on_delete=models.CASCADE, db_index=True,
        db_column="nutii", related_name='nut2'
    )


class Concelhos(models.Model):
    """
    Concelhos
    """

    fid    = models.AutoField(primary_key=True)
    code   = models.CharField(max_length=6, unique=True)
    name   = models.CharField(max_length=200, unique=True)
    geom   = models.MultiPolygonField(srid=3763)
    nutiii = models.ForeignKey(
        Nutsiii, on_delete=models.CASCADE, db_index=True,
        db_column='nutiii', related_name='conc'
    )


class Freguesias(models.Model):
    """
    Freguesias
    """

    fid   = models.AutoField(primary_key=True)
    code  = models.CharField(max_length=6, unique=True)
    name  = models.CharField(max_length=200)
    geom  = models.MultiPolygonField(srid=3763)
    munid = models.ForeignKey(
        Concelhos, on_delete=models.CASCADE, db_index=True,
        db_column="munid", related_name="freg"
    )


class IneBgri(models.Model):
    """
    Seccoes e subseccoes estatisticas
    """

    fid  = models.AutoField(primary_key=True)
    code = models.CharField(max_length=11, unique=True)
    lugid = models.CharField(max_length=15)
    lugname = models.CharField(max_length=50)
    geom = models.PolygonField(srid=3763)
    freg = models.ForeignKey(
        Freguesias, on_delete=models.CASCADE, db_index=True,
        db_column="freg", related_name='bgris'
    )


class Places(models.Model):
    """
    Places in Portugal
    """

    fid = models.AutoField(primary_key=True)
    lugid = models.CharField(max_length=15)
    lugname = models.CharField(max_length=100)
    altname = models.CharField(max_length=100, null=True, blank=True)
    geom = models.PointField(srid=3763)

    freg = models.ForeignKey(
        Freguesias, on_delete=models.CASCADE, db_index=True,
        db_column="freg", related_name='placefreg'
    )

    source = models.CharField(max_length=50)
