from datetime import timedelta, date, datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models

from app.settings import AUTH_USER_MODEL
from swimpro.models import Facility


class TrainingGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)
    members = models.ManyToManyField(
        'Person',
        related_name='group',
        through='TrainingGroupMembership'
    )

    class Meta:
        db_table = 'training_group'

    def __str__(self):
        return self.short_name


class TrainingPlan(models.Model):
    """Defines the repeating rule (e.g., 'Every Monday 18:00')."""
    group = models.ForeignKey(TrainingGroup, on_delete=models.CASCADE, related_name="plans")
    coach = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='plans')
    location = models.ForeignKey(Facility, on_delete=models.SET_NULL, null=True, related_name='plans')

    # Recurrence settings
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # None means infinite
    frequency_days = models.IntegerField(default=7)  # 7 = weekly, 1 = daily

    # Time slot
    start_time = models.TimeField()
    duration_minutes = models.IntegerField(default=60)


    def __str__(self):
        return f"{self.group.name} ({self.start_time})"

    class Meta:
        db_table = 'training_plan'
        ordering = ['-start_date']


class PlanException(models.Model):
    """
    Defines a break or override that can apply to ONE or MANY plans.
    Supports single-day or multi-day timespans (e.g., 'Christmas Break 2024').
    """
    TYPE_CHOICES = [
        ('SKIP', _('Holiday / Cancelled')),
        ('OVERRIDE', _('Time Change')),
    ]

    # The Many-to-Many relationship
    plans = models.ManyToManyField(
        TrainingPlan,
        related_name='exceptions',
        help_text=_("Select all training plans affected by this exception.")
    )
    reason = models.CharField(max_length=200, blank=True, help_text=_("e.g., 'School Holiday', 'Coach Sick'"))
    exception_type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    # Timespan support
    start_date = models.DateField(help_text=_("First affected date"))
    end_date = models.DateField(null=True, blank=True, help_text=_("Last affected date (leave empty for single-day)"))

    # If OVERRIDE, store new time
    new_start_time = models.DateTimeField(null=True, blank=True)
    new_duration = models.IntegerField(null=True, blank=True)

    def clean(self):
        """Validate that end_date >= start_date if provided."""
        from django.core.exceptions import ValidationError
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': _("End date cannot be before start date.")})

    def __str__(self):
        if self.end_date:
            return f"{self.reason} ({self.start_date} - {self.end_date})"
        return f"{self.reason} ({self.start_date})"

    class Meta:
        db_table = 'plan_exception'
        verbose_name_plural = _("Plan Exceptions")


class TrainingSession(models.Model):
    class Type(models.TextChoices):
        TRAINING = 'TRAIN', _('Training')
        COMPETITION = 'COMP', _('Competition')
        OTHER = 'OTH', _('Other')

    """The actual instance. Generated dynamically or manually."""
    plan = models.ForeignKey(TrainingPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    name = models.CharField(max_length=200, default="Undefined")
    start = models.DateTimeField()
    end = models.DateTimeField()

    # Specific data for THIS session
    location = models.ForeignKey('swimpro.Facility', on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    type = models.CharField(choices=Type, default=Type.TRAINING, max_length=10)
    notes = models.TextField(blank=True)
    is_cancelled = models.BooleanField(default=False)

    # Attendance tracking (Many-to-Many if swimmers can vary per session)
    attendees = models.ManyToManyField('swimpro.Person', through='Attendance', blank=True)

    class Meta:
        db_table = 'training_session'
        unique_together = ['plan', 'start', 'end']
        ordering = ['-start']

    def __str__(self):
        status = _(" (Cancelled)" )if self.is_cancelled else ""
        return f"{self.start.strftime("%A %d.%m.%Y %H:%M")} - {status}"

    @property
    def duration(self) -> timedelta:
        return  self.end - self.start



class Attendance(models.Model):
    """Link table for session attendance with extra data (e.g., score, notes)."""
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    swimmer = models.ForeignKey('swimpro.Person', on_delete=models.CASCADE)
    score = models.IntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    attended = models.BooleanField(default=False)
    excused = models.BooleanField(default=None, null=True, blank=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ['session', 'swimmer']

    def save(
        self,
        *,
        force_insert = False,
        force_update = False,
        using = None,
        update_fields = None,
    ):
        # Enforce mutual exclusivity
        if self.attended and self.excused:
            # Both True - prioritize attended, set excused to False
            self.excused = False
        elif self.excused and not self.attended:
            # excused is True, attended is False - this is valid
            pass
        elif not self.attended and self.excused is None:
            # attended is False, excused is None - set excused to False for clarity
            self.excused = False

        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def clean(self):
        """Validation for forms/admin"""
        super().clean()
        if self.attended and self.excused:
            raise ValidationError(
                'Attendance and excused status cannot both be True.'
            )