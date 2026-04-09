from django.contrib import admin

from swimpro.models import *


admin.site.register(Accreditation)

admin.site.register(TrainingGroupMembership)

admin.site.register(TrainingGroup)
admin.site.register(TrainingPlan)
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


@admin.register(PlanException)
class PlanExceptionAdmin(admin.ModelAdmin):
    list_display = ('reason', 'start_date', 'end_date', 'exception_type', 'plan_count')
    filter_horizontal = ('plans',)
    list_filter = ('exception_type',)

    def plan_count(self, obj):
        return obj.plans.count()

    plan_count.short_description = "Affected Plans"

    fieldsets = (
        (None, {
            'fields': ('reason', 'exception_type', 'plans')
        }),
        ('Timespan', {
            'fields': ('start_date', 'end_date'),
            'description': 'Leave end_date empty for single-day exceptions'
        }),
        ('Override Details (only for OVERRIDE type)', {
            'fields': ('new_start_time', 'new_duration'),
            'classes': ('collapse',)
        }),
    )