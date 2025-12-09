from datetime import datetime

from django.db import models
from recurrence.fields import RecurrenceField


class TrainingGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=15)

    class Meta:
        db_table = 'training_group'


class TrainingTime(models.Model):
    id = models.AutoField(primary_key=True)
    training_time = models.DateTimeField()
    group = models.ForeignKey("TrainingGroup", on_delete=models.CASCADE)
    place = models.ForeignKey("swimpro.Facility",null=True, on_delete=models.SET_NULL)
    duration = models.DurationField()
    recurrences = RecurrenceField()

    class Meta:
        db_table = 'training_time'


class TrainingSession(models.Model):
    id = models.AutoField(primary_key=True)
    training_time = models.ForeignKey("TrainingTime", on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now)
    plan = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'training_session'


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    training = models.ForeignKey("TrainingSession", on_delete=models.CASCADE)
    person = models.ForeignKey("swimpro.Person", on_delete=models.CASCADE)

    attended = models.BooleanField(default=False)
    lane = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'attendance'