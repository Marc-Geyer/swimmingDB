import enum

from django.contrib.auth.models import User
from django.db import models
from nanoid_field import NanoidField
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='person')
    name = models.CharField(max_length=200)
    privilege_level = models.PositiveSmallIntegerField(
        choices=[
            (1, "Viewer"),
            (2, "Editor"),
            (3, "Manager"),
            (4, "Admin"),
        ],
        default=1,
    )
    birthday = models.DateField()

    class Meta:
        db_table = 'person'

    def __str__(self):
        return self.name


class Accreditation(models.Model):
    class Type(models.TextChoices):
        FIRST_AID = 'FA', _('First Aid')
        RESCUE_ABILITY = 'RE', _('Rescue ability')
        LIFEGUARD = 'LI', _('Lifeguard')
        C_TRAININGS_LICENSE = 'CL', _('C-Training license')
        B_TRAININGS_LICENSE = 'BL', _('B-Training license')
        A_TRAININGS_LICENSE = 'AL', _('A-Training license')

    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    Person = models.ForeignKey("Person", on_delete=models.CASCADE)
    type = models.CharField(max_length=2, choices=Type)
    date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'accreditation'
