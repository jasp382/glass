from django.contrib.gis.db      import models
from django.contrib.auth.models import User

# Create your models here.

class UserAttr(models.Model):
    slug = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=50)
    atype = models.CharField(max_length=50)


class UserAttrValue(models.Model):
    attr = models.ForeignKey(
        UserAttr, on_delete=models.CASCADE, db_index=True,
        db_column='attr'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column="user", related_name='attr'
    )
    value = models.CharField(max_length=250)

    def __str__(self):
        return self.value


class UserCodes(models.Model):
    """
    Confirmation tokens sended to Users
    """

    fid     = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True,
        db_column='user_id', related_name='token'
    )

    token = models.CharField(max_length=50, unique=True)
    confirmation = models.BooleanField(default=False)

    def __str__(self):
        return self.token


class Organizations(models.Model):
    alias    = models.CharField(max_length=10, unique=True)
    name     = models.CharField(max_length=100)
    address  = models.CharField(max_length=200, null=True, blank=True)
    city     = models.CharField(max_length=20, null=True, blank=True)
    state    = models.CharField(max_length=50, null=True, blank=True)
    postal   = models.CharField(max_length=20, null=True, blank=True)
    country  = models.CharField(max_length=50, null=True, blank=True)
    countryi = models.CharField(max_length=8, null=True, blank=True)
    phone    = models.IntegerField(null=True, blank=True)
    email    = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

