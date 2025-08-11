from django.contrib import admin
from .models import Task, PomodoroSession

admin.site.register(Task)
admin.site.register(PomodoroSession)
