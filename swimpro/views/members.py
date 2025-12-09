from django.shortcuts import render

from swimpro.models import Person
from swimpro.views.util import get_entries


def members(request):
    persons = get_entries(Person, {}, ['sir_name','name'])

    context = {'persons': persons}

    return render(request, "members.html", context=context)
