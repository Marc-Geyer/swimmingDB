from datetime import datetime

from django.db import models
from recurrence.fields import RecurrenceField


class TrainingGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)
    members = models.ManyToManyField(
        'Person',
        related_name='groups',
        through='TrainingGroupMembership'
    )

    class Meta:
        db_table = 'training_group'

    def __str__(self):
        return self.short_name


class TrainingTime(models.Model):
    id = models.AutoField(primary_key=True)
    training_time = models.DateTimeField()
    group = models.ForeignKey("TrainingGroup", on_delete=models.CASCADE)
    place = models.ForeignKey("swimpro.Facility",null=True, on_delete=models.SET_NULL)
    duration = models.DurationField()
    recurrences = RecurrenceField()

    class Meta:
        db_table = 'training_time'

    def __str__(self):
        return f"{self.training_time} [{self.group}] ({self.place})"


class TrainingSession(models.Model):
    id = models.AutoField(primary_key=True)
    training_time = models.ForeignKey("TrainingTime", on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.now)
    plan = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'training_session'

    def __str__(self):
        return f"{self.training_time.group} [{self.datetime}]"


class Attendance(models.Model):
    id = models.AutoField(primary_key=True)
    training = models.ForeignKey("TrainingSession", on_delete=models.CASCADE)
    person = models.ForeignKey("swimpro.Person", on_delete=models.CASCADE)

    attended = models.BooleanField(default=False)
    lane = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'attendance'

    def __str__(self):
        return f"{self.training} [{self.person}]"