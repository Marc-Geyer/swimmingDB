from django.shortcuts import render

from swimpro.models import Person
from swimpro.views.util import get_entries
from swimpro.utils.permissions import require_privilege


@require_privilege(1)
def members(request):
    persons = get_entries(Person, {}, ['name'])

    context = {'persons': persons}

    return render(request, "members.html", context=context)
