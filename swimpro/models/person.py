import enum

from django.db import models
from nanoid_field import NanoidField
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=100)
    sir_name = models.CharField(max_length=100)
    birthday = models.DateField()

    class Meta:
        db_table = 'person'


class Accreditation(models.Model):
    class Type(models.TextChoices):
        FIRST_AID = 'FA', _('First Aid')
        RESCUE_ABILITY = 'RE', _('Rescue ability')
        LIFEGUARD = 'LI', _('Lifeguard')
        C_TRAININGS_LICENSE = 'CL', _('C-Training license')
        B_TRAININGS_LICENSE = 'BL', _('B-Training license')
        A_TRAININGS_LICENSE = 'AL', _('A-Training license')

    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    Person = models.ForeignKey('Person', on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=Type)