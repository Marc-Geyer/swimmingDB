from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse

from datetime import date, timedelta
from django.utils import timezone

from swimpro.models import TrainingSession

@login_required
def calendar_view(request):
    return render(request, 'calendar.html')


@login_required
def calendar_data(request):
    """
    API endpoint to fetch sessions for a specific range.
    Query params: start_date, end_date
    """
    try:
        start_str = request.GET.get('start_date')
        end_str = request.GET.get('end_date')

        if not start_str or not end_str:
            # Default to current month if not provided
            today = timezone.now().date()
            start = today.replace(day=1)
            end = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        else:
            start = date.fromisoformat(start_str)
            end = date.fromisoformat(end_str)

        sessions = TrainingSession.objects.filter(
            start__gte=start,
            end__lte=end
        ).select_related('plan').order_by('start')

        data = []
        for s in sessions:
            data.append({
                'id': s.id,
                'title': f"{s.plan.group.name} Training" if s.plan else s.name,
                'start': f"{s.start.isoformat()}",
                'end': f"{s.end.isoformat()}",
                'allDay': False,
                'extendedProps': {
                    'is_cancelled': s.is_cancelled,
                    'location': f"{s.location}",
                    'type': s.type,
                    'notes': s.notes,
                    'plan_id': s.plan.id if s.plan else None
                },
                'className': 'cancelled' if s.is_cancelled else ''
            })

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)