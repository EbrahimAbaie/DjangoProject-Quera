from django.db import models

from apps.workspaces.models import Workspace
from core.models import TimestampedModel


class Tag(TimestampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=20, default="#64748b")

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "name"),
                condition=models.Q(is_deleted=False),
                name="unique_tag_name_per_workspace",
            ),
        ]

    def __str__(self):
        return self.name
