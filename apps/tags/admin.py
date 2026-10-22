from django.contrib import admin

from core.admins.base import SoftDeleteAdmin

from .models import Tag


@admin.register(Tag)
class TagAdmin(SoftDeleteAdmin):
    list_display = ("workspace", "name", "color")
    search_fields = ("name",)
    list_filter = ("workspace",)
    ordering = ("-created_at",)
