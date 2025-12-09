from django.db import models
from django.utils.translation import gettext_lazy as _

class City(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField()

    class Meta:
        db_table = 'city'


class Facility(models.Model):
    class Types(models.TextChoices):
        INDOOR_50M = 'ID50', _('Indoor swimming track 50m')
        OUTDOOR_50M = 'OD50', _('Outdoor swimming track 50m')
        INDOOR_25M = 'ID25', _('Indoor swimming track 25m')
        OUTDOOR_25M = 'OD25', _('Outdoor swimming track 25m')
        ATHLETIC_INDOOR = 'ATID', _('Indoor athletic track')
        ATHLETIC_OUTDOOR = 'ATOD', _('Outdoor athletic track')
        OTHER = 'OTH', _('Other')

    id = models.AutoField(primary_key=True)
    name = models.CharField()
    type = models.CharField(choices=Types.choices, max_length=10)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    postal_code = models.IntegerField()
    street_address = models.TextField()

    class Meta:
        db_table = 'facility'


