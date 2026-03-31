from django.shortcuts import render

from swimpro.models import TrainingSession, TrainingTime
from swimpro.utils.permissions import require_privilege
from swimpro.views.util import get_entries


@require_privilege(1)
def sessions(request):
    person = request.person

    training_times = get_entries(TrainingTime, {})
    training_sessions = get_entries(TrainingSession, {})

    context = {"person": person, "times": training_times, "sessions": training_sessions}

    return render(request, "members.html", context=context)
