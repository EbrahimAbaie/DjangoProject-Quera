from django.db import models

from apps.workspaces.models import Workspace
from core.models import TimestampedModel
from core.models.base import SoftDeleteManager, SoftDeleteQuerySet


class TagQuerySet(SoftDeleteQuerySet):
    def visible_to(self, user):
        if not getattr(user, "is_authenticated", False):
            return self.none()
        return self.filter(
            workspace__memberships__user=user,
            workspace__memberships__is_active=True,
            workspace__memberships__is_deleted=False,
        ).distinct()


class Tag(TimestampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=20, default="#64748b")

    objects = SoftDeleteManager.from_queryset(TagQuerySet)()
    all_objects = TagQuerySet.as_manager()

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
