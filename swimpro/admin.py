from django.contrib import admin

from swimpro.models import *

admin.site.register(Accreditation)

admin.site.register(TrainingGroupMembership)
admin.site.register(UserPerson)


admin.site.register(TrainingGroup)
admin.site.register(TrainingPlan)
admin.site.register(TrainingSession)
admin.site.register(Attendance)

admin.site.register(City)
admin.site.register(Facility)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    def get_linked_users_with_relation(self, obj):
        """Returns 'Username (Relation)' for each link."""
        # Query the through model directly to get the relation field
        links = UserPerson.objects.filter(person=obj).select_related('user')

        if not links.exists():
            return "-"

        parts = []
        for link in links:
            username = link.user.username
            relation_label = link.get_relation_display()  # Gets "Self", "Child", etc.
            parts.append(f"{username} ({relation_label})")

        return ", ".join(parts)

    # Configure the display settings for the method
    get_linked_users_with_relation.short_description = "Users & Relations"
    get_linked_users_with_relation.admin_order_field = 'user__username'  # Optional: allows sorting by this column
    get_linked_users_with_relation.allow_tags = True  # Deprecated in newer Django, but harmless if kept for compatibility

    list_display = (
        "first_name",
        "last_name",
        "birth_date",
        "e_mail",
        "get_linked_users_with_relation"
    )

    list_filter = (
        "first_name",
        "last_name",
        "birth_date",
    )

    ordering = ('last_name', 'first_name')

    search_fields = ("first_name", "last_name", "e_mail", "user__username")


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