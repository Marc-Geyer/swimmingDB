from datetime import datetime, timedelta
from typing import Dict, Generator, Optional, List
from django.db.models import QuerySet, Q
from django.utils import timezone

from swimpro.models import TrainingSession, TrainingGroup, TrainingPlan, PlanException


def generate_planned_sessions(
        start_dt: datetime,
        end_dt: datetime,
        plan_id: Optional[int] = None,
        group_id: Optional[int] = None,
        include_exceptions: bool = True
) -> Generator[Dict, None, None]:
    """
    Generates a stream of planned training sessions based on a TrainingPlan,
    respecting PlanExceptions.

    Args:
        plan_id: Filter by specific plan ID.
        group_id: Filter by group ID (fetches all plans for this group).
        start_dt: Start of the generation window (inclusive).
        end_dt: End of the generation window (inclusive).
        include_exceptions: If True, applies SKIP/OVERRIDE logic. 
                            If False, returns raw recurrence ignoring exceptions.

    Yields:
        Dict containing event data suitable for FullCalendar or DB insertion.
    """

    # 1. Determine which Plans to process
    plans_qs = TrainingPlan.objects.all()
    if plan_id:
        plans_qs = plans_qs.filter(id=plan_id)
    elif group_id:
        plans_qs = plans_qs.filter(group_id=group_id)

    # Ensure we have the necessary related objects loaded for efficiency
    plans_qs = plans_qs.select_related('group', 'coach', 'location')

    for plan in plans_qs:
        # 2. Calculate the recurrence range
        # If plan has an end_date, cap it. Otherwise, use the query end_dt.
        plan_end = plan.end_date if plan.end_date else end_dt.date()
        effective_end = min(plan_end, end_dt.date())

        if plan.start_date > effective_end:
            continue

        # 3. Fetch exceptions for this plan within the relevant window
        # We fetch exceptions that overlap with our generation window
        exceptions_qs = PlanException.objects.filter(plans=plan)
        if include_exceptions:
            # Optimization: Only fetch exceptions that could possibly affect the range
            # An exception affects the range if: exception.start <= query_end AND exception.end >= query_start
            exceptions_qs = exceptions_qs.filter(
                Q(end_date__gte=start_dt.date()) | Q(end_date__isnull=True),
                start_date__lte=end_dt.date(),
            ).order_by('start_date')

        exceptions_list = list(exceptions_qs)

        # 4. Iterate through dates
        current_date = plan.start_date
        while current_date <= effective_end:
            # Check if current_date is covered by any exception
            active_exception = None
            if include_exceptions:
                for exc in exceptions_list:
                    exc_end = exc.end_date if exc.end_date else current_date  # Infinite exceptions extend to current check
                    if exc.start_date <= current_date <= exc_end:
                        active_exception = exc
                        break

            if active_exception:
                if active_exception.exception_type == 'SKIP':
                    # Skip this date entirely
                    current_date += timedelta(days=plan.frequency_days)
                    continue
                elif active_exception.exception_type == 'OVERRIDE':
                    # Handle override: use new time if provided, otherwise keep original?
                    # Assuming OVERRIDE implies a change. If new_start_time is null, maybe skip?
                    # Or treat as a standard session with modified time.
                    # Let's assume if new_start_time exists, we use it.
                    if active_exception.new_start_time:
                        # Parse the override time
                        override_dt = active_exception.new_start_time
                        # Adjust duration if provided
                        duration = active_exception.new_duration or plan.duration_minutes
                        yield _create_event_dict(plan, override_dt, duration, is_override=True)
                        current_date += timedelta(days=plan.frequency_days)
                        continue

            # Standard Generation
            # Combine plan start_date with plan start_time
            session_dt = timezone.make_aware(datetime.combine(current_date, plan.start_time))

            # Ensure session is within the requested query window
            if session_dt >= start_dt and session_dt <= end_dt:
                yield _create_event_dict(plan, session_dt, plan.duration_minutes, is_override=False)

            current_date += timedelta(days=plan.frequency_days)


def _create_event_dict(plan: TrainingPlan, start_dt: datetime, duration_minutes: int,
                       is_override: bool = False) -> Dict:
    """Helper to format a single event into a dictionary."""
    end_dt = start_dt + timedelta(minutes=duration_minutes)

    # Map to FullCalendar fields
    event = {
        "id": f"planned_{plan.id}_{start_dt.timestamp()}",  # Unique ID for generated events
        "title": f"{plan.group.short_name} - {plan.group.name}",
        "start": start_dt.isoformat(),
        "end": end_dt.isoformat(),
        "extendedProps": {
            "plan_id": plan.id,
            "group_id": plan.group.id,
            "coach": plan.coach.get_full_name() if plan.coach else "No Coach",
            "location": plan.location.name if plan.location else "TBD",
            "is_generated": True,
            "is_override": is_override,
            "original_plan_time": str(plan.start_time)
        }
    }

    if plan.location:
        event["location"] = plan.location.address or plan.location.name

    return event


def generate_full_calendar_events(
        start_dt: datetime,
        end_dt: datetime,
        plan_id: Optional[int] = None,
        group_id: Optional[int] = None,
        include_exceptions: bool = True
) -> List[Dict]:
    """
    Convenience wrapper that returns a list of events ready for FullCalendar.
    """
    return list(generate_planned_sessions(
        plan_id=plan_id,
        group_id=group_id,
        start_dt=start_dt,
        end_dt=end_dt,
        include_exceptions=include_exceptions
    ))


def get_existing_sessions(
        start_dt: datetime,
        end_dt: datetime,
        plan_id: Optional[int] = None,
        group_id: Optional[int] = None,
) -> List[Dict]:
    """
    Fetches actual TrainingSession objects from the DB that fall within the range.
    Useful for merging with generated events to show 'realized' vs 'planned'.
    """
    qs = TrainingSession.objects.filter(start__gte=start_dt, end__lte=end_dt)

    if plan_id:
        qs = qs.filter(plan_id=plan_id)
    elif group_id:
        # Join through plan to group
        qs = qs.filter(plan__group_id=group_id)

    qs = qs.select_related('plan', 'plan__group', 'plan__coach', 'location')

    events = []
    for session in qs:
        events.append({
            "id": f"session_{session.id}",
            "title": session.name or f"{session.plan.group.short_name} Session",
            "start": session.start.isoformat(),
            "end": session.end.isoformat(),
            "extendedProps": {
                "session_id": session.id,
                "type": session.type,
                "is_cancelled": session.is_cancelled,
                "notes": session.notes,
                "is_generated": False
            },
            "color": "#ff0000" if session.is_cancelled else "#007bff"  # Example coloring
        })

    return events


def merge_and_render_events(
        start_dt: datetime,
        end_dt: datetime,
        plan_id: Optional[int] = None,
        group_id: Optional[int] = None,
        include_exceptions: bool = True
) -> List[Dict]:
    """
    Merges generated planned events (respecting exceptions) with existing DB sessions.
    Returns a unified list for FullCalendar.

    Logic:
    1. Generate planned events.
    2. Fetch existing sessions.
    3. If an existing session exists for a planned slot, it might override the visual representation
       (e.g., showing attendance or cancellation status).
    """
    planned = generate_full_calendar_events(
        plan_id=plan_id,
        group_id=group_id,
        start_dt=start_dt,
        end_dt=end_dt,
        include_exceptions=include_exceptions
    )

    existing = get_existing_sessions(
        plan_id=plan_id,
        group_id=group_id,
        start_dt=start_dt,
        end_dt=end_dt
    )

    # Create a map of existing sessions by their approximate start time to merge data
    # Note: In a real app, you might want to match by exact time or ID if you stored the link
    existing_map = {}
    for ex in existing:
        # Key by start time string for simplicity
        existing_map[ex['start']] = ex

    final_events = []
    for p in planned:
        # Check if there's a corresponding real session
        if p['start'] in existing_map:
            real = existing_map[p['start']]
            # Merge: Use real session data but keep context that it was planned
            merged = {**real, "extendedProps": {**real['extendedProps'], "was_planned": True}}
            final_events.append(merged)
        else:
            final_events.append(p)

    # Add any existing sessions that weren't in the planned list (manual entries)
    planned_starts = {e['start'] for e in planned}
    for ex in existing:
        if ex['start'] not in planned_starts:
            final_events.append(ex)

    return final_events

