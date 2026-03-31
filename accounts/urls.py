from django.urls import path, include

from .views import register, CustomPasswordResetView

app_name = "auth"

urlpatterns = [
    path("signup/", register, name="signup"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("", include("django.contrib.auth.urls")),
]