import logging
import traceback

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.http import JsonResponse

from datetime import date, timedelta, datetime
from django.utils import timezone
from django.views.decorators.http import require_GET

from swimpro.models import TrainingSession, TrainingGroup
from swimpro.views.calendar_events import merge_and_render_events

logger = logging.getLogger(__name__)
User = get_user_model()


@login_required
def calendar_view(request):
    return render(request, 'calendar.html')



@login_required
@require_GET
def calendar_data(request):
    if request.user.is_authenticated:
        user = request.user
    else:
        user = None

    try:
        # Parse date range
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')

        start = datetime.fromisoformat(start_str) if start_str else timezone.now() - timedelta(days=60)
        end = datetime.fromisoformat(end_str) if end_str else timezone.now() + timedelta(days=60)

        events = merge_and_render_events(start_dt=start, end_dt=end)

        return JsonResponse(events, safe=False)

    except Exception as e:
        # Log error in production
        print(f"Calendar Error: {e}")
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)