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
        fields = ("username", "email", "role", "privilege_level")


# 2. Admin-Klasse erstellen
@admin.register(SwimProUser)
class SwimProUserAdmin(BaseUserAdmin):
    form = SwimProUserChangeForm
    add_form = SwimProUserCreationForm

    # Spalten in der Übersicht (List View)
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "privilege_level",
        "is_active",
        "is_staff",
        "date_joined"
    )

    # Filter in der rechten Seitenleiste
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        "role",
        "privilege_level",
        "groups"
    )

    # Suchfelder (oben rechts)
    search_fields = ("username", "email", "first_name", "last_name")

    # Sortierung standardmäßig nach Benutzernamen
    ordering = ("username",)

    # Felder, die beim Erstellen angezeigt werden
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "email", "password1", "password2", "role", "privilege_level"),
            },
        ),
    )

    # Felder, die beim Bearbeiten angezeigt werden (in Blöcken gruppiert)
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "SwimPro Profile",
            {
                "fields": ("role", "privilege_level", "pending_email", "email_verification_pending"),
            },
        ),
    )

    # Optional: Verhindern, dass Superuser gelöscht werden können
    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_superuser:
            return False
        return super().has_delete_permission(request, obj)