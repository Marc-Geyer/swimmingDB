from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from swimpro.models import Person
from swimpro.views.util import get_entries


@login_required
def members(request):
    persons = get_entries(Person, {}, ['last_name'])

    context = {'persons': persons}

    return render(request, "members.html", context=context)
