from django.db import models
from nanoid_field import NanoidField


class Person(models.Model):
    id = NanoidField(max_length=20, primary_key=True, unique=True, editable=False)
    name = models.CharField(max_length=100)
    sir_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'person'
