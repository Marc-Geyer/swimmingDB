from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from swimpro.models import *


class ProfileInline(admin.StackedInline):
    model = Person
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = ("username", "email", "is_active", "get_approved")

    def get_approved(self, obj):
        return obj.userprofile.is_approved
    get_approved.boolean = True
    get_approved.short_description = "Approved"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Register your models here.
admin.site.register(Person)
admin.site.register(Accreditation)

admin.site.register(TrainingGroup)
admin.site.register(TrainingTime)
admin.site.register(TrainingSession)
admin.site.register(Attendance)

admin.site.register(City)
admin.site.register(Facility)
