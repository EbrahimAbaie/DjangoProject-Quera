from django.contrib import admin

from core.admins.base import SoftDeleteAdmin

from .models import Project


@admin.register(Project)
class ProjectAdmin(SoftDeleteAdmin):
    list_display = ("workspace", "name", "client", "is_archived")
    search_fields = ("name",)
    list_filter = ("workspace",)
    ordering = ("-created_at",)
