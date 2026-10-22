from datetime import timedelta

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from apps.projects.models import Project
from apps.time_entries.admin import TimeEntryAdmin
from apps.time_entries.models import TimeEntry
from apps.users.models import User
from apps.workspaces.models import Workspace


class TimeEntryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(mobile="09123333333")
        self.other_user = User.objects.create_user(mobile="09124444444")
        self.workspace = Workspace.objects.create(
            name="First workspace",
            owner=self.user,
        )
        self.other_workspace = Workspace.objects.create(
            name="Second workspace",
            owner=self.user,
        )

    def test_running_returns_only_active_unfinished_entries(self):
        now = timezone.now()
        running = TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.user,
            start_time=now,
        )
        TimeEntry.objects.create(
            workspace=self.other_workspace,
            user=self.user,
            start_time=now,
            end_time=now + timedelta(minutes=10),
        )
        deleted = TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.other_user,
            start_time=now,
        )
        deleted.delete()

        self.assertEqual(list(TimeEntry.objects.running()), [running])

    def test_only_one_running_entry_is_allowed_per_user_and_workspace(self):
        TimeEntry.objects.create(workspace=self.workspace, user=self.user)

        with self.assertRaises(IntegrityError), transaction.atomic():
            TimeEntry.objects.create(workspace=self.workspace, user=self.user)

    def test_save_calculates_duration_and_duration_seconds(self):
        started_at = timezone.now()
        entry = TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.user,
            start_time=started_at,
            end_time=started_at + timedelta(seconds=90),
        )

        self.assertEqual(entry.duration, timedelta(seconds=90))
        self.assertEqual(entry.duration_seconds, 90)

    def test_stop_validates_saves_and_returns_entry(self):
        started_at = timezone.now()
        ended_at = started_at + timedelta(minutes=5)
        entry = TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.user,
            start_time=started_at,
        )

        result = entry.stop(ended_at=ended_at)

        self.assertIs(result, entry)
        self.assertEqual(entry.end_time, ended_at)
        self.assertEqual(entry.duration, timedelta(minutes=5))

    def test_project_must_belong_to_same_workspace(self):
        project = Project.objects.create(
            workspace=self.other_workspace,
            name="Other project",
        )
        entry = TimeEntry(
            workspace=self.workspace,
            user=self.user,
            project=project,
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Project must belong to the same workspace.",
        ):
            entry.clean()

    def test_end_time_must_be_after_start_time(self):
        started_at = timezone.now()
        entry = TimeEntry(
            workspace=self.workspace,
            user=self.user,
            start_time=started_at,
            end_time=started_at - timedelta(seconds=1),
        )

        with self.assertRaisesMessage(
            ValidationError,
            "End time must be after start time.",
        ):
            entry.clean()

    def test_admin_configuration(self):
        model_admin = TimeEntryAdmin(TimeEntry, admin.site)

        self.assertEqual(
            model_admin.list_display,
            ("workspace", "user", "project", "start_time", "end_time"),
        )
        self.assertEqual(model_admin.search_fields, ("description",))
        self.assertEqual(
            model_admin.list_filter,
            ("workspace", "project", "start_time"),
        )
        self.assertEqual(model_admin.ordering, ("-created_at",))
