from django.urls import path, include

from .views import register, CustomPasswordResetView, activate_account, account_settings

app_name = "auth"

urlpatterns = [
    path("signup/", register, name="signup"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('settings', account_settings, name="settings"),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("", include("django.contrib.auth.urls")),
]