from django.core.exceptions import ValidationError
from django.db import models

from apps.clients.models import Client
from apps.workspaces.models import Workspace
from core.models import TimestampedModel


class Project(TimestampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=20, default="#2563eb")
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "name"),
                condition=models.Q(is_deleted=False),
                name="unique_project_name_per_workspace",
            ),
        ]

    def clean(self):
        super().clean()
        if self.client_id and self.client.workspace_id != self.workspace_id:
            raise ValidationError("Client must belong to the same workspace.")

    def __str__(self):
        return self.name
