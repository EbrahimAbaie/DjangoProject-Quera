from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.projects.models import Project
from apps.tags.models import Tag
from apps.workspaces.models import Workspace
from core.models import TimestampedModel
from core.models.base import SoftDeleteManager, SoftDeleteQuerySet


class TimeEntryQuerySet(SoftDeleteQuerySet):
    def running(self):
        return self.filter(end_time__isnull=True)


class TimeEntry(TimestampedModel):
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_entries",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="time_entries")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    is_billable = models.BooleanField(default=False)

    objects = SoftDeleteManager.from_queryset(TimeEntryQuerySet)()
    all_objects = TimeEntryQuerySet.as_manager()

    class Meta:
        verbose_name_plural = "time entries"
        ordering = ["-start_time", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("workspace", "user"),
                condition=models.Q(end_time__isnull=True, is_deleted=False),
                name="unique_running_entry_per_user_workspace",
            ),
        ]

    @property
    def duration_seconds(self):
        if self.duration is None:
            return None
        return self.duration.total_seconds()

    def clean(self):
        super().clean()
        if self.project_id and self.project.workspace_id != self.workspace_id:
            raise ValidationError("Project must belong to the same workspace.")
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError("End time must be after start time.")

    def save(self, *args, **kwargs):
        if self.end_time and self.start_time:
            self.duration = max(self.end_time - self.start_time, timedelta())
        else:
            self.duration = None
        return super().save(*args, **kwargs)

    def stop(self, ended_at=None):
        self.end_time = ended_at or timezone.now()
        self.full_clean()
        self.save()
        return self

    def __str__(self):
        return f"{self.user} - {self.start_time}"
