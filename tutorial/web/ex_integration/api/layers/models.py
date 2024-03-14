from django.db import models

# Create your models here.

class Layers(models.Model):
    """
    Layers Model
    """

    alias  = models.CharField(max_length=15, unique=True)
    design = models.CharField(max_length=100)
    style  = models.CharField(max_length=100, null=True, blank=True)
