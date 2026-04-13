from django.contrib.auth.views import LogoutView, PasswordResetView

from django.urls import path

from .views import *

app_name = "swimpro"

urlpatterns = [
    path("", index.index, name="index"),
    path("test-ws/", index.websocket_test,  name="websocket_test"),
    path("members", members.members, name="members"),
    path("calendar/", calendar.calendar_view, name="calendar"),

    path("api/calendar-data/", calendar.calendar_data, name="calendar_data"),
]


