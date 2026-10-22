from django.contrib import admin

from core.admins.base import SoftDeleteAdmin

from .models import TimeEntry


@admin.register(TimeEntry)
class TimeEntryAdmin(SoftDeleteAdmin):
    list_display = ("workspace", "user", "project", "start_time", "end_time")
    search_fields = ("description",)
    list_filter = ("workspace", "project", "start_time")
    ordering = ("-created_at",)
