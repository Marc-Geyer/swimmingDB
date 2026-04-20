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

    def get_occurrence_dates(self, max_future_days=180):
        """
        Generator yielding all occurrence datetimes for this plan,
        respecting frequency and end_date, but NOT exceptions yet.
        """
        if not self.start_date:
            return

        current_date = self.start_date
        end_limit = self.end_date or (date.today() + timedelta(days=max_future_days))

        # Ensure we don't go beyond the end_limit
        while current_date <= end_limit:
            # Combine date with plan time
            try:
                dt = datetime.combine(current_date, self.start_time)
                yield dt
            except ValueError:
                # Handle invalid time combinations if necessary
                pass

            current_date += timedelta(days=self.frequency_days)

    def get_exceptions_for_date_range(self, start_date, end_date):
        """
        Fetches exceptions that overlap with the given date range.
        Returns a list of exception objects.
        """
        # Exceptions apply if:
        # (exception.start <= range.end) AND (exception.end >= range.start OR exception.end is null)
        from django.db.models import Q

        return self.exceptions.filter(
            Q(end_date__gte=start_date) | Q(end_date__isnull=True),
            start_date__lte=end_date
        )

    def generate_events_with_exceptions(self, group_short_name, max_future_days=180):
        """
        Returns a list of event dictionaries for FullCalendar.
        Handles the logic of generating dates, checking exceptions,
        and avoiding duplicates with existing sessions.
        """
        events = []
        today = date.today()
        end_range = today + timedelta(days=max_future_days)

        # 1. Generate all potential dates
        potential_dates = list(self.get_occurrence_dates(max_future_days))

        if not potential_dates:
            return events

        # 2. Fetch all relevant exceptions for the entire range in one query
        # We need exceptions that touch ANY part of our generated range
        exceptions = self.get_exceptions_for_date_range(potential_dates[0].date(), potential_dates[-1].date())

        # Create a lookup map for faster exception checking: date -> list of exceptions
        exception_map = {}
        for exc in exceptions:
            # Determine the range of dates this exception covers
            exc_start = exc.start_date
            exc_end = exc.end_date or exc.start_date

            # We only care about dates within our potential_dates list
            for dt in potential_dates:
                d = dt.date()
                if exc_start <= d <= exc_end:
                    if d not in exception_map:
                        exception_map[d] = []
                    exception_map[d].append(exc)

        # 3. Check for existing sessions to avoid duplicates
        # Fetch all sessions for this plan within the date range
        # We filter by start time being within the range
        start_dt = potential_dates[0]
        end_dt = potential_dates[-1] + timedelta(days=1)  # Include the last day

        existing_sessions = TrainingSession.objects.filter(
            plan=self,
            start__gte=start_dt,
            start__lt=end_dt
        ).values_list('start', flat=True)

        existing_start_times = set(existing_sessions)

        # 4. Build the events
        for dt in potential_dates:
            event_date = dt.date()

            # Check for exceptions on this specific date
            day_exceptions = exception_map.get(event_date, [])

            skip = False
            override_time = None
            override_duration = None

            for exc in day_exceptions:
                if exc.exception_type == 'SKIP':
                    skip = True
                    break
                elif exc.exception_type == 'OVERRIDE':
                    # If multiple overrides exist, the last one in the list wins (or you can add logic to merge)
                    override_time = exc.new_start_time.time() if exc.new_start_time else self.start_time
                    override_duration = exc.new_duration or self.duration_minutes

            if skip:
                continue

            # Calculate final times
            final_start_time = override_time or self.start_time
            final_duration = override_duration or self.duration_minutes

            event_start = datetime.combine(event_date, final_start_time)
            event_end = event_start + timedelta(minutes=final_duration)

            # Skip if a session already exists for this exact start time
            if event_start in existing_start_times:
                continue

            # Construct the event dictionary
            location_name = self.location.name if self.location else "TBD"
            title = f"{group_short_name} - {location_name}"

            events.append({
                "title": title,
                "start": event_start.isoformat(),
                "end": event_end.isoformat(),
                "allDay": False,
                "extendedProps": {
                    "db_id": None,
                    "type": "calculated",
                    "plan_id": self.id,
                    "group_id": self.group.id,
                    "group_short_name": group_short_name,
                    "is_generated": True,
                    "notes": "Generated from Plan",
                    "original_time": self.start_time.isoformat() if hasattr(self.start_time, 'isoformat') else str(
                        self.start_time),
                    "has_override": override_time is not None
                }
            })

        return events

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

    def affected_dates(self):
        """
        Generator yielding all dates covered by this exception.
        Returns single date if end_date is None.
        """
        from datetime import timedelta
        current = self.start_date
        end = self.end_date or self.start_date

        while current <= end:
            yield current
            current += timedelta(days=1)

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