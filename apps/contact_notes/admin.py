from django.contrib import admin

from core.admins.base import SoftDeleteAdmin

from .models import ContactNote


@admin.register(ContactNote)
class ContactNoteAdmin(SoftDeleteAdmin):
    list_display = ("name", "email", "is_reviewed", "created_at")
    search_fields = ("name", "email", "message")
    list_filter = ("is_reviewed", "created_at")
    ordering = ("-created_at",)
