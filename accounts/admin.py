from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from accounts.models import SwimProUser


class SwimProUserChangeForm(UserChangeForm):
    class Meta:
        model = SwimProUser
        fields = "__all__"


class SwimProUserCreationForm(UserCreationForm):
    class Meta:
        model = SwimProUser
        fields = ("username", "email")


# 2. Admin-Klasse erstellen
@admin.register(SwimProUser)
class SwimProUserAdmin(BaseUserAdmin):
    form = SwimProUserChangeForm
    add_form = SwimProUserCreationForm

    # columns
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "date_joined"
    )

    # filters
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "groups"
    )

    # searchable fields
    search_fields = ("username", "email", "first_name", "last_name")

    # sorting
    ordering = ("username",)

    # fields, shown oon object creation
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2",),
            },
        ),
    )

    # Felder, die beim Bearbeiten angezeigt werden (in Blöcken gruppiert)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "SwimPro Profile",
            {
                "fields": ("pending_email", "email_verification_pending"),
            },
        ),
    )

    # Prevent superuser deletion
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)