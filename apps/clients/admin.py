from django.contrib import admin

from core.admins.base import SoftDeleteAdmin

from .models import Client


@admin.register(Client)
class ClientAdmin(SoftDeleteAdmin):
    list_display = ("workspace", "name")
    search_fields = ("name",)
    list_filter = ("workspace",)
    ordering = ("-created_at",)
