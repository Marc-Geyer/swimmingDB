from datetime import date, timedelta, time, datetime
from django.db.models import Q

from swimpro.models import TrainingSession, PlanException


def calculate_end(start_input, duration) -> time:
    """
        Calculates the end time given a start time (str, time, or datetime)
        and a duration (timedelta).

        Args:
            start_input: Can be a string (ISO format), a datetime object, or a time object.
            duration: A timedelta object representing the duration to add.

        Returns:
            A datetime object if start was a datetime or string.
            A time object if start was a time object (handles day rollover logic).
        """

    # 1. Normalize the start input
    if isinstance(start_input, str):
        # Try parsing ISO format (YYYY-MM-DDTHH:MM:SS) or standard datetime string
        try:
            start_dt = datetime.fromisoformat(start_input)
        except ValueError:
            # Fallback for common formats like "2024-04-09 14:30:00"
            start_dt = datetime.strptime(start_input, "%Y-%m-%d %H:%M:%S")
        return start_dt + duration

    elif isinstance(start_input, datetime):
        return start_input + duration

    elif isinstance(start_input, time):
        # If only a time is provided, we need a dummy date to perform the addition
        # We use today's date as a placeholder
        today = date.today()
        start_dt = datetime.combine(today, start_input)

        end_dt = start_dt + duration

        # If the result crosses midnight, the date part will change.
        # We return the time part, but note that the "day" has effectively shifted.
        return end_dt.time()

    else:
        raise TypeError("start_input must be a string, datetime, or time object.")


def generate_sessions_for_plan(plan, days_ahead=30):
    """
    Generates sessions for a specific plan, checking PlanException timespans.
    """
    current_date = plan.start_date
    end_limit = date.today() + timedelta(days=days_ahead)

    if plan.end_date and plan.end_date < end_limit:
        end_limit = plan.end_date

    while current_date <= end_limit:
        # Check if current_date falls within ANY exception timespan for this plan
        exception = PlanException.objects.filter(
            plans=plan,
            start_date__lte=current_date,
            end_date__gte=current_date  # NULL end_date handled below
        ).first()

        # Handle single-day exceptions (end_date IS NULL)
        if not exception:
            exception = PlanException.objects.filter(
                plans=plan,
                start_date=current_date,
                end_date__isnull=True
            ).first()

        if exception:
            if exception.exception_type == 'SKIP':
                current_date += timedelta(days=plan.frequency_days)
                continue

            if exception.exception_type == 'OVERRIDE':
                start_t = exception.new_start_time or plan.start_time
                dur = exception.new_duration or plan.duration_minutes

                TrainingSession.objects.update_or_create(
                    plan=plan, session_date=current_date,
                    defaults={
                        'start_time': start_t,
                        'end_time': calculate_end(start_t, dur),
                        'notes': f"Override: {exception.reason}"
                    }
                )

        else:
            TrainingSession.objects.update_or_create(
                plan=plan, session_date=current_date,
                defaults={
                    'start_time': plan.start_time,
                    'end_time': calculate_end(plan.start_time, plan.duration_minutes),
                    'is_cancelled': False
                }
            )

        current_date += timedelta(days=plan.frequency_days)