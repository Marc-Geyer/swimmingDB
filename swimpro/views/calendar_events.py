import asyncio
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
from django.db.models import QuerySet
from django.utils import timezone

from swimpro.models import TrainingGroup, TrainingPlan, PlanException, TrainingSession

async def generate_calendar_events(group_queryset: QuerySet[TrainingGroup]) -> List[Dict[str, Any]]:
    """
    Generates a list of FullCalendar-compatible event dictionaries from TrainingGroups.

    Handles:
    1. Existing TrainingSessions (highest priority).
    2. Calculated future events from TrainingPlans using recurrence logic.
    3. PlanExceptions (Skip or Override).

    Args:
        group_queryset: A queryset of TrainingGroup objects.

    Returns:
        A list of dicts ready for JSON serialization and posting to FullCalendar.
    """

    events = []
    today = timezone.now().date()
    # Look ahead 6 months for generated events if no session exists
    end_range = today + timedelta(days=180)

    # Fetch all related data in bulk to minimize DB hits
    async for group in group_queryset.prefetch_related(
            'plans__exceptions',
            'plans__sessions'
    ):
        # 1. Process existing Sessions (Concrete events)
        plan_ids = [p.id for p in group.plans.all()]

        # Async fetch for sessions
        sessions_qs = TrainingSession.objects.filter(plan_id__in=plan_ids).filter(start__gte=today)
        async for session in sessions_qs:
            event = _session_to_event(session)
            events.append(event)

        # 2. Process Plans for Future/Calculated Events
        # We use the model method to generate events cleanly
        async for plan in group.plans.all():
            # Call the model helper method
            # Note: This method is synchronous in the model, but we are in an async context.
            # If the model method does heavy DB queries internally, wrap it in sync_to_async.
            # However, since we are iterating and the DB calls inside are likely optimized,
            # we can run it directly if the DB driver supports async, or wrap it.

            # To be safe with Django ORM in async context:
            from asgiref.sync import sync_to_async

            # We need to pass the group_short_name
            group_short_name = group.short_name

            # Run the synchronous model method in a thread pool
            plan_events = await sync_to_async(plan.generate_events_with_exceptions)(
                group_short_name=group_short_name,
                max_future_days=180
            )

            events.extend(plan_events)

    return events


def _session_to_event(session: TrainingSession) -> Dict[str, Any]:
    """Converts a TrainingSession model instance to a FullCalendar event dict."""
    title = session.name
    if session.type == TrainingSession.Type.COMPETITION:
        title = f"[COMP] {title}"
    elif session.is_cancelled:
        title = f"CANCELLED: {title}"

    return {
        "title": title,
        "start": session.start.isoformat(),
        "end": session.end.isoformat(),
        "allDay": False,
        "backgroundColor": "#ff4d4d" if session.is_cancelled else "#28a745",  # Visual cue
        "borderColor": "#ff4d4d" if session.is_cancelled else "#28a745",
        "extendedProps": {
            "db_id": session.id,
            "type": "session",
            "plan_id": session.plan.id if session.plan else None,
            "group_id": session.plan.group.id if session.plan else None,
            "notes": session.notes,
            "is_cancelled": session.is_cancelled,
            "attendees_count": session.attendees.count()
        }
    }
