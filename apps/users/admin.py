from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "mobile",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    search_fields = ("mobile", "email", "first_name", "last_name")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("mobile",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("mobile", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "birth_date",
                    "description",
                    "profile_picture",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("mobile", "password1", "password2"),
            },
        ),
    )
