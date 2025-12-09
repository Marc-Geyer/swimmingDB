from django.contrib import admin

from swimpro.models import *

# Register your models here.

admin.site.register(Person)
admin.site.register(Accreditation)

admin.site.register(TrainingGroup)
admin.site.register(TrainingTime)
admin.site.register(TrainingSession)
admin.site.register(Attendance)

admin.site.register(City)
admin.site.register(Facility)
