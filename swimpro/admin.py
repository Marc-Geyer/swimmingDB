from django.contrib import admin

from swimpro.models import *

# Register your models here.


admin.site.register(Accreditation)

admin.site.register(TrainingGroupMembership)

admin.site.register(TrainingGroup)
admin.site.register(TrainingTime)
admin.site.register(TrainingSession)
admin.site.register(Attendance)

admin.site.register(City)
admin.site.register(Facility)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "last_name",
        "birth_date",
        "e_mail",
        "user"
    )

    list_filter = (
        "name",
        "last_name",
        "birth_date",
    )

    ordering = ("user",)

    search_fields = ("name", "last_name", "e_mail", )