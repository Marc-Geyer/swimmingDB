from django.db import models
from django.utils import timezone
from nanoid_field import NanoidField
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from app.settings import AUTH_USER_MODEL


class Person(models.Model):
    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='persons',
        null=True, blank=True)
    name = models.CharField(max_length=200, default="")
    last_name = models.CharField(max_length=200, default="")
    birth_date = models.DateField(null=True, blank=True)
    e_mail = models.EmailField(null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)

    class Meta:
        db_table = 'person'

    def __str__(self):
        return f"{self.name} {self.last_name}"

    def get_age(self) -> int:
        """
        Calculates the exact age in years based on the current local date.
        Returns 0 if birth_date is not set.
        """
        if not self.birth_date:
            return 0

        today = timezone.localdate()
        age = today.year - self.birth_date.year

        # Adjust if birthday hasn't happened yet this year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1

        return age


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
