from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.http import JsonResponse

from datetime import date, timedelta
from django.utils import timezone
from django.views.decorators.http import require_GET

from swimpro.models import TrainingSession, TrainingGroup
from swimpro.views.calendar_events import generate_calendar_events


@login_required
def calendar_view(request):
    return render(request, 'calendar.html')



@login_required
@require_GET
async def calendar_data(request):
    """
    API endpoint returning ALL events (Sessions + Calculated Plans) for the requested range.
    Optimized to use the generate_calendar_events function.
    """
    try:
        # Parse date range
        start_str = request.GET.get('start_date')
        end_str = request.GET.get('end_date')

        if not start_str or not end_str:
            # Default to current month
            today = timezone.now().date()
            start = today.replace(day=1)
            # Get last day of current month
            if today.month == 12:
                end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        else:
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)

        # 1. Fetch all groups (User specific logic will be added later: e.g., Group.objects.filter(members=user))
        # For now, fetch all groups as requested
        group_qs = TrainingGroup.objects.all()

        # 2. Generate events using the helper function
        # We wrap the async function call since we are in an async view
        all_events = await generate_calendar_events(group_qs)

        # 3. Filter events by the requested date range on the backend (optional but recommended for large datasets)
        # FullCalendar can handle this, but filtering reduces payload size
        filtered_events = []
        for event in all_events:
            event_start = event['start'][:10] # Extract YYYY-MM-DD
            if start <= date.fromisoformat(event_start) <= end:
                filtered_events.append(event)

        return JsonResponse(filtered_events, safe=False)

    except Exception as e:
        # Log error in production
        print(f"Calendar Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)