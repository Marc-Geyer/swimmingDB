from django.contrib.auth.views import LogoutView, PasswordResetView

from django.urls import path

from .views import *

app_name = "swimpro"

urlpatterns = [
    path("", index.index, name="index"),
    # path("login/", login.LoginView.as_view(), name="login"),
    # path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    path("members", members.members, name="members"),
    path("session/", sessions.sessions, name="session"),
]


