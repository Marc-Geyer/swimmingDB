from django.urls import path, include

from .views import register, CustomPasswordResetView, activate_account, account_settings, email_change, \
    email_change_verify, email_change_confirmation, username_change, CustomPasswordChangeView, \
    CustomPasswordResetConfirmView

app_name = "auth"

urlpatterns = [
    path("signup/", register, name="signup"),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('email_change', email_change, name='email_change'),
    path('email_change/done', email_change_confirmation, name='email_change_done'),
    path('email_change/<uidb64>/<token>/', email_change_verify, name='email_change_verify'),
    path('username_change', username_change, name='username_change'),
    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path("password_change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("reset/<uidb64>/<token>/", CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("settings", account_settings, name="settings"),
    path("", include("django.contrib.auth.urls")),
]