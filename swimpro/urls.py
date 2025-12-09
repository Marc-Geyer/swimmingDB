from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import *

urlpatterns = [
    path("", index.index, name="index"),

    # login / logout
    path("login/", login.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),

    # register
    path("register/", login.RegisterView.as_view(), name="register"),

    # password reset
    path("reset-password/", login.PasswordResetRequestView.as_view(), name="reset_password"),
    path("reset-password/<uidb64>/<token>/", login.password_reset_verify, name="password_reset_verify"),

    # admin approval
    path("admin/approve-users/", login.approve_users, name="approve_users"),

    path("members", members.members, name="members"),
]


