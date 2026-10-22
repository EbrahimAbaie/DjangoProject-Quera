from django.conf import settings
from django.db import models

from core.models import TimestampedModel


class Workspace(TimestampedModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="workspaces/", blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_workspaces",
    )

    class Meta:
        ordering = ["name", "created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("owner", "name"),
                condition=models.Q(is_deleted=False),
                name="unique_workspace_name_per_owner",
            ),
        ]

    def __str__(self):
        return self.name


class WorkspaceMembership(TimestampedModel):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["workspace__name", "user__mobile"]
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "user"),
                condition=models.Q(is_deleted=False),
                name="unique_workspace_membership",
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.workspace}"
