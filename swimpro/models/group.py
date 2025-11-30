from django.db import models
from recurrence.fields import RecurrenceField


class TrainingsGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=15)

    class Meta:
        db_table = 'training_group'

class TrainingTime(models.Model):
    id = models.AutoField(primary_key=True)
    training_time = models.DateTimeField()
    duration = models.DurationField()
    recurrences = RecurrenceField()

    class Meta:
        db_table = 'training_time'