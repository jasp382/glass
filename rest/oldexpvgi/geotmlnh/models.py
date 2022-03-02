from django.contrib.gis.db import models

# Create your models here.
class geonames(models.Model):
    """
    Geo Names List
    """
    
    fid     = models.IntegerField(primary_key=True)
    geoname = models.CharField(max_length=200)
    what_is = models.CharField(max_length=20)


class wordgrp(models.Model):
    """
    Words Groups
    """
    
    fid = models.IntegerField(primary_key=True)
    desc = models.CharField(max_length=50)


class words(models.Model):
    """
    Interest Words
    """
    
    fid = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=50)
    grp_id = models.ForeignKey(
        'wordgrp', on_delete=models.CASCADE, db_index=True,
        db_column='grp_id'
    )


class facepages(models.Model):
    """
    Face Pages list
    """
    
    fid       = models.IntegerField(primary_key=True)
    face_id   = models.CharField(max_length=20)
    page_name = models.CharField(max_length=20)


class facedata(models.Model):
    """
    Face Collected Data
    """
    
    post_id      = models.CharField(max_length=50, primary_key=True)
    description  = models.CharField(max_length=7000, blank=True, null=True)
    message      = models.CharField(max_length=18000, blank=True, null=True)
    link         = models.CharField(max_length=500, blank=True, null=True)
    datahora     = models.CharField(max_length=20, blank=True, null=True)
    #page_ref     = models.ForeignKey(
        #'facepages', on_delete=models.CASCADE, db_index=True,
        #db_column='page_ref'
    #)
    page_ref     = models.CharField(max_length=20, blank=True, null=True)
    type         = models.CharField(max_length=20, blank=True, null=True)
    story        = models.CharField(max_length=200, blank=True, null=True)
    place_id     = models.DecimalField(
        max_digits=20, decimal_places=4, blank=True, null=True)
    place_name   = models.CharField(max_length=100, blank=True, null=True)
    city         = models.CharField(max_length=50, blank=True, null=True)
    country      = models.CharField(max_length=50, blank=True, null=True)
    latitude     = models.DecimalField(
        max_digits=20, decimal_places=4, blank=True, null=True
    ); longitude = models.DecimalField(
        max_digits=20, decimal_places=4, blank=True, null=True)
    street       = models.CharField(max_length=200, blank=True, null=True)
    zip          = models.CharField(max_length=50, blank=True, null=True)
    state        = models.CharField(max_length=20, blank=True, null=True)
    located_in   = models.DecimalField(
        max_digits=20, decimal_places=4, blank=True, null=True
    )
    fidref = models.ForeignKey(
        'refdata', on_delete=models.CASCADE, db_index=True,
        db_column='fidref', related_name="fb",
        blank=True, null=True
    )


class flickrdata(models.Model):
    """
    Data Extracted from Flickr
    """
    
    fid        = models.CharField(max_length=50, primary_key=True)
    title      = models.CharField(max_length=300, blank=True, null=True)
    descriptio = models.CharField(max_length=300, blank=True, null=True)
    url        = models.CharField(max_length=200, blank=True, null=True)
    datetaken  = models.CharField(max_length=20, blank=True, null=True)
    dateupload = models.CharField(max_length=20, blank=True, null=True)
    keyword    = models.CharField(max_length=50, blank=True, null=True)
    geom       = models.PointField(srid=3763, blank=True, null=True)


class twitterdata(models.Model):
    """
    Data Extracted from Twitter
    """
    
    fid           = models.BigIntegerField(primary_key=True)
    txt           = models.CharField(max_length=500)
    tlang         = models.CharField(max_length=5, blank=True, null=True)
    userid        = models.BigIntegerField(blank=True, null=True)
    username      = models.CharField(max_length=50, blank=True, null=True)
    url           = models.CharField(max_length=200, blank=True, null=True)
    keyword       = models.CharField(max_length=50, blank=True, null=True)
    latitude      = models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True
    );longitude= models.DecimalField(
        max_digits=10, decimal_places=4, blank=True, null=True)
    userloc = models.CharField(max_length=200, blank=True, null=True)
    placename     = models.CharField(max_length=50, blank=True, null=True)
    placecountry  = models.CharField(max_length=20, blank=True, null=True)
    placecountryc = models.CharField(max_length=20, blank=True, null=True)
    placebox      = models.CharField(max_length=200, blank=True, null=True)
    placeid       = models.CharField(max_length=20, blank=True, null=True)
    daytime       = models.CharField(max_length=20, blank=True, null=True)
    followersn    = models.BigIntegerField()


class jornals(models.Model):
    """
    List of Web Jornals
    """
    
    fid       = models.IntegerField(primary_key=True)
    name      = models.CharField(max_length=20)
    url       = models.CharField(max_length=100)
    title     = models.CharField(max_length=100)
    corpus    = models.CharField(max_length=100)
    csscls    = models.CharField(max_length=500, blank=True, null=True)
    forbidden = models.CharField(max_length=500, blank=True, null=True)


class news(models.Model):
    """
    News in Online Journals
    """
    
    fid = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    wgrp_id = models.ForeignKey(
        'wordgrp', on_delete=models.CASCADE, db_index=True,
        db_column='wgrp_id'
    )
    jrn_id  = models.ForeignKey(
        'jornals', on_delete=models.CASCADE, db_index=True,
        db_column='jrn_id'
    )


class news_txt(models.Model):
    """
    News Text
    """
    
    fid     = models.IntegerField(primary_key=True)
    news_id = models.ForeignKey(
        'news', on_delete=models.CASCADE, db_index=True,
        db_column='news_id'
    )
    norder  = models.IntegerField()
    txt     = models.CharField(max_length=10000)



"""
Reference Data and Samples
"""

class fevents(models.Model):
    """
    Fire Events List
    """
    
    fid    = models.IntegerField(primary_key=True)
    event  = models.CharField(max_length=500)
    tstart = models.DateField()
    tend   = models.DateField(blank=True, null=True)


class lyrevents(models.Model):
    """
    Layer List for Each Event
    """
    
    fid    = models.IntegerField(primary_key=True)
    name   = models.CharField(max_length=200)
    geosrv = models.CharField(max_length=50)
    style  = models.CharField(max_length=50)
    event  = models.ForeignKey(
        'fevents', on_delete=models.CASCADE, db_index=True,
        db_column='event', related_name='lyr'
    )


class lyrpolygon(models.Model):
    """
    Geometry for Layer Polygons
    """
    
    fid = models.IntegerField(primary_key=True)
    cat = models.CharField(max_length=200)
    geom = models.PolygonField(srid=3763)
    lyrid = models.ForeignKey(
        'lyrevents', on_delete=models.CASCADE, db_index=True,
        db_column='lyrid'
    )


class refdata(models.Model):
    """
    Facedata samples
    """
    
    fid    = models.IntegerField(primary_key=True)
    postid = models.ForeignKey(
        'facedata', on_delete=models.CASCADE, db_index=True,
        db_column='postid', related_name='fbrow'
    )
    
    is_fire     = models.IntegerField()
    is_fire_bin = models.IntegerField()
    is_fire_evn = models.ForeignKey(
        'fevents', on_delete=models.CASCADE, db_index=True,
        db_column='is_fire_evn', related_name='contrib'
    )


class refdatatxt(models.Model):
    """
    Ref data cleaned text
    """
    
    fid  = models.IntegerField(primary_key=True)
    rid  = models.ForeignKey(
        'refdata', on_delete=models.CASCADE, db_index=True,
        db_column='rid'
    )
    full_pp = models.CharField(max_length=10000)
    txt_pp  = models.CharField(max_length=10000)


"""
Tables to store info about classification models
"""

class classi(models.Model):
    """
    Classification's attempts list
    """
    
    fid        = models.CharField(max_length=10, primary_key=True)
    nb_acc     = models.DecimalField(max_digits=7, decimal_places=3)
    nb_mdl     = models.CharField(max_length=500)
    nb_vec     = models.CharField(max_length=500)
    rf_acc     = models.DecimalField(max_digits=7, decimal_places=3)
    rf_mdl     = models.CharField(max_length=500)
    rf_vec     = models.CharField(max_length=500)
    svm_acc    = models.DecimalField(max_digits=7, decimal_places=3)
    svm_mdl    = models.CharField(max_length=500)
    svm_vec    = models.CharField(max_length=500)
    logreg_acc = models.DecimalField(max_digits=7, decimal_places=3)
    logreg_mdl = models.CharField(max_length=500)
    daytime    = models.DateTimeField()


class class_res(models.Model):
    """
    Classification results by classification process and iteration
    """
    
    fid    = models.CharField(max_length=14, primary_key=True)
    cls_id = models.ForeignKey(
        'classi', on_delete=models.CASCADE, db_index=True,
        db_column='cls_id'
    )
    mdl    = models.CharField(max_length=50)
    mdlfil = models.CharField(max_length=500)
    vect   = models.CharField(max_length=500)
    acc    = models.DecimalField(decimal_places=3, max_digits=7)
    err    = models.DecimalField(decimal_places=3, max_digits=7)
    tpr    = models.DecimalField(decimal_places=3, max_digits=7)
    tnr    = models.DecimalField(decimal_places=3, max_digits=7) 
    ppr    = models.DecimalField(decimal_places=3, max_digits=7) 
    fpr    = models.DecimalField(decimal_places=3, max_digits=7)


class class_train(models.Model):
    """
    List train used in classification's
    """
    
    fid = models.IntegerField(primary_key=True)
    fid_cls = models.ForeignKey(
        'class_res', on_delete=models.CASCADE, db_index=True,
        db_column='fid_cls'
    )
    fid_ref = models.ForeignKey(
        'refdata', on_delete=models.CASCADE, db_index=True, db_column="fid_ref"
    )


class class_test(models.Model):
    """
    List test used in classification's
    """
    
    fid = models.IntegerField(primary_key=True)
    fid_cls = models.ForeignKey(
        'class_res', on_delete=models.CASCADE, db_index=True,
        db_column='fid_cls'
    )
    fid_ref = models.ForeignKey(
        'refdata', on_delete=models.CASCADE, db_index=True, db_column="fid_ref"
    )
    classification = models.IntegerField()