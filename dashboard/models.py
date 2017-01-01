from __future__ import unicode_literals

from django.db import models

class Measurement(models.Model):
    time = models.DateTimeField(primary_key=True)
    temperature = models.DecimalField(max_digits=3, decimal_places=1)

    class Meta:
       get_latest_by = 'time'

class DailySummary(models.Model):
    day = models.DateField(primary_key=True)
    minimum = models.FloatField()
    maximum = models.FloatField()
    
    class Meta:
        managed = False