from django.contrib.gis.db import models

# Create your models here.


class GeoServerCon(models.Model):
    """
    Parameters to Connect to GeoServer
    """
    
    fid = models.IntegerField(primary_key=True)
    host = models.CharField(max_length=30)
    port = models.CharField(max_length=4)
    protocol = models.CharField(max_length=7)
    workspace = models.CharField(max_length=10)


class Countries(models.Model):
    """
    Countries Table
    """
    
    fid       = models.BigIntegerField(primary_key=True)
    slug      = models.CharField(max_length=7)
    descricao = models.CharField(max_length=255)


class Scale(models.Model):
    """
    Scale's Table
    """
    
    fid   = models.BigIntegerField(primary_key=True)
    desig = models.CharField(max_length=50)
    id_grp = models.ForeignKey(
        'Countries', on_delete=models.CASCADE, db_index=True,
        db_column='id_grp', related_name='scale'
    )


class StudyCases(models.Model):
    """
    Table to record Study Cases
    """
    
    fid       = models.BigIntegerField(primary_key=True)
    slug      = models.CharField(max_length=7)
    descricao = models.CharField(max_length=250)
    
    geom      = models.PolygonField(srid=4326)
    top       = models.DecimalField(max_digits=20, decimal_places=12)
    bottom    = models.DecimalField(max_digits=20, decimal_places=12)
    left      = models.DecimalField(max_digits=20, decimal_places=12)
    right     = models.DecimalField(max_digits=20, decimal_places=12)
    
    geom_ctx  = models.PolygonField(srid=4326, blank=True, null=True)
    top_ctx   = models.DecimalField(max_digits=20, decimal_places=12)
    bottom_ctx= models.DecimalField(max_digits=20, decimal_places=12)
    left_ctx  = models.DecimalField(max_digits=20, decimal_places=12)
    right_ctx = models.DecimalField(max_digits=20, decimal_places=12)
    
    country   = models.ForeignKey(
        'Countries', on_delete=models.DO_NOTHING, db_index=True,
        db_column='country', related_name='statgrp'
    )
    
    gstore    = models.CharField(max_length=7)


class ThemeLyr(models.Model):
    """
    Indicators table
    """
    
    fid  = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=10)
    unit = models.CharField(max_length=20)


class Years(models.Model):
    """
    Years Table
    """
    
    fid  = models.IntegerField(primary_key=True)
    year = models.IntegerField()


class StatUnit(models.Model):
    """
    Statistic Units
    """
    
    fid     = models.AutoField(primary_key=True)
    id_unit = models.CharField(max_length=11)
    design  = models.CharField(max_length=250, blank=True, null=True)
    geom    = models.MultiPolygonField(srid=3763)
    
    up_unit = models.CharField(max_length=11)
    up_name = models.CharField(max_length=250, blank=True, null=True)
    up_tipo = models.CharField(max_length=30, blank=True, null=True)
    
    country = models.ForeignKey(
        'Countries', on_delete=models.CASCADE, db_index=True,
        db_column='country', related_name="stats", blank=True, null=True
    )
    
    scale = models.ForeignKey(
        'Scale', on_delete=models.CASCADE, db_index=True,
        db_column='scale'
    )


class StatCase(models.Model):
    """
    Relation between statistic Units and Study Cases
    
    Features are related when a stat unit is contained by the interest area
    of an study case
    """
    
    fid = models.AutoField(primary_key=True)
    fidcase = models.ForeignKey(
        'StudyCases', on_delete=models.CASCADE, db_index=True,
        db_column='fidcase', related_name='gcases'
    )
    fidunit = models.ForeignKey(
        'StatUnit', on_delete=models.CASCADE, db_index=True,
        db_column='fidunit', related_name='gstats'
    )


class UploadData(models.Model):
    """
    Record data send by users
    """
    
    fid      = models.BigIntegerField(primary_key=True)
    filename = models.CharField(max_length=100)
    utiliza  = models.IntegerField()
    case     = models.ForeignKey(
        'StudyCases', on_delete=models.CASCADE, db_index=True,
        db_column='case', blank=True, null=True
    )
    ctx_name = models.CharField(max_length=100, blank=True, null=True)


class UploadCols(models.Model):
    """
    Columns names in data send by users
    """
    
    fid = models.BigIntegerField(primary_key=True)
    rqst_id = models.ForeignKey(
        'UploadData', on_delete=models.CASCADE, db_index=True,
        db_column='rqst_id', related_name='cols'
    )
    idx_col = models.IntegerField()
    name_col = models.CharField(max_length=50)
    ctx_col  = models.BooleanField()


class SldStyles(models.Model):
    """
    Style Layer Descriptor list
    """
    
    fid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=12)


class SldRules(models.Model):
    """
    Style rules
    """
    
    fid     = models.AutoField(primary_key=True)
    red     = models.IntegerField()
    green   = models.IntegerField()
    blue    = models.IntegerField()
    opacity = models.IntegerField()
    order   = models.IntegerField(blank=True, null=True)
    quality = models.CharField(blank=True, null=True, max_length=50)
    style   = models.ForeignKey(
        'SldStyles', on_delete=models.CASCADE, 
        db_index=True, db_column='style', related_name='sldrules'
    )
    stk_red   = models.IntegerField()
    stk_green = models.IntegerField()
    stk_blue  = models.IntegerField()


class LyrIndicators(models.Model):
    """
    Layers in the application
    """
    
    fid     = models.BigIntegerField(primary_key=True)
    id_case = models.ForeignKey(
        'StudyCases', on_delete=models.CASCADE, db_index=True,
        db_column='id_case', related_name='lyrs'
    )
    id_indicator = models.ForeignKey(
        'ThemeLyr', on_delete=models.CASCADE, db_index=True,
        db_column='id_indicator'
    )
    
    id_year  = models.ForeignKey(
        'Years', on_delete=models.CASCADE, db_index=True,
        db_column='id_year', related_name='lyr_year'
    )
    
    min_val  = models.DecimalField(max_digits=15, decimal_places=3)
    max_val  = models.DecimalField(max_digits=15, decimal_places=3)
    mean_val = models.DecimalField(max_digits=15, decimal_places=3)
    
    style = models.CharField(max_length=50)


class LyrIndicatorsCls(models.Model):
    """
    Layers Classes
    """
    
    fid     = models.AutoField(primary_key=True)
    id_lyr  = models.ForeignKey(
        'LyrIndicators', on_delete=models.CASCADE, db_index=True,
        db_column='id_lyr', related_name="lyr_cls"
    )
    order   = models.IntegerField()
    cat_val = models.CharField(max_length=100)
    color   = models.CharField(max_length=8)
    ctx_val = models.CharField(max_length=100)


class IndValues(models.Model):
    """
    Indicators Values
    """
    
    fid = models.AutoField(primary_key=True)
    
    id_unit = models.ForeignKey(
        'StatUnit', on_delete=models.CASCADE, db_index=True,
        db_column="id_unit"
    )
    
    id_lyr = models.ForeignKey(
        'LyrIndicators', on_delete=models.CASCADE, db_index=True,
        db_column='id_lyr', related_name="lyr_vals"
    )
    
    value = models.DecimalField(max_digits=15, decimal_places=3)
    cls   = models.IntegerField()


class IndCtxValues(models.Model):
    """
    Context Map: Indicators Values
    """
    
    fid = models.AutoField(primary_key=True)
    
    id_unit = models.ForeignKey(
        'StatUnit', on_delete=models.CASCADE, db_index=True,
        db_column="id_unit"
    )
    
    id_lyr = models.ForeignKey(
        'LyrIndicators', on_delete=models.CASCADE, db_index=True,
        db_column="id_lyr", related_name="lyr_ctx_vals"
    )
    
    value = models.DecimalField(max_digits=15, decimal_places=3)
    cls   = models.IntegerField()


"""
Point Data
"""

class PntLyr(models.Model):
    """
    Points Layer
    """
    
    fid  = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=100, blank=True, null=True)
    
    idcase = models.ForeignKey(
        'StudyCases', on_delete=models.CASCADE, db_index=True,
        db_column='idcase', related_name='pntlyrs'
    )


class PntCols(models.Model):
    """
    Columns of Points Layer
    """
    
    fid  = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    lyrid = models.ForeignKey(
        "PntLyr", on_delete=models.CASCADE, db_index=True,
        db_column="lyrid", related_name='cols'
    )


class PntGeom(models.Model):
    """
    Points Geometry
    """
    
    fid = models.IntegerField(primary_key=True)
    geom = models.PointField(srid=4326, blank=True, null=True)
    lyrid = models.ForeignKey(
        "PntLyr", on_delete=models.CASCADE, db_index=True,
        db_column="lyrid", related_name='geomlyr'
    )


class PntData(models.Model):
    """
    Points Data
    """
    
    fid = models.IntegerField(primary_key=True)
    col = models.ForeignKey(
        "PntCols", on_delete=models.CASCADE, db_index=True,
        db_column="col"
    )
    geomid = models.ForeignKey(
        'PntGeom', on_delete=models.CASCADE, db_index=True,
        db_column="geomid"
    )
    data = models.CharField(max_length=500)


"""
Polygon Data
"""

class PolygonLyr(models.Model):
    """
    Polygon Layers
    """
    
    fid  = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    fidcase = models.ForeignKey(
        'StudyCases', on_delete=models.CASCADE, db_index=True,
        db_column='fidcase', related_name='pollyrs'
    )


class PolygonCols(models.Model):
    """
    Columns Name of Polygon Layers
    """
    
    fid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    idlyr = models.ForeignKey(
        'PolygonLyr', on_delete=models.CASCADE, db_index=True,
        db_column='idlyr'
    )


class PolygonGeom(models.Model):
    """
    Polygon Geometry
    """
    
    fid  = models.IntegerField(primary_key=True)
    geom = models.PolygonField(srid=3763, blank=True, null=True)
    idlyr = models.ForeignKey(
        'PolygonLyr', on_delete=models.CASCADE, db_index=True,
        db_column='idlyr'
    )


class PolygonData(models.Model):
    """
    Polygon Data
    """
    
    fid  = models.IntegerField(primary_key=True)
    colfid = models.ForeignKey(
        'PolygonCols', on_delete=models.CASCADE, db_index=True,
        db_column='colfid'
    )
    geomfid = models.ForeignKey(
        'PolygonGeom', on_delete=models.CASCADE, db_index=True,
        db_column='geomfid'
    )
    data = models.CharField(max_length=500)

