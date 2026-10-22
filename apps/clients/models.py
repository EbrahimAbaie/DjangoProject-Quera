from django.db import models

from apps.workspaces.models import Workspace
from core.models import TimestampedModel


class Client(TimestampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="clients",
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to="clients/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "name"),
                condition=models.Q(is_deleted=False),
                name="unique_client_name_per_workspace",
            ),
        ]

    def __str__(self):
        return self.name
