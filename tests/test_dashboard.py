from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.projects.models import Project
from apps.time_entries.models import TimeEntry
from apps.users.models import User
from apps.workspaces.models import Workspace, WorkspaceMembership


class DashboardPreviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(mobile="09120000006")
        self.other_user = User.objects.create_user(mobile="09120000007")
        self.member = User.objects.create_user(mobile="09120000008")
        self.inactive_member = User.objects.create_user(mobile="09120000009")

        self.workspace = Workspace.objects.create(
            name="Visible workspace",
            owner=self.user,
        )
        self.hidden_workspace = Workspace.objects.create(
            name="Hidden workspace",
            owner=self.other_user,
        )
        WorkspaceMembership.objects.create(
            workspace=self.workspace,
            user=self.member,
            role=WorkspaceMembership.Role.MEMBER,
        )
        WorkspaceMembership.objects.create(
            workspace=self.workspace,
            user=self.inactive_member,
            role=WorkspaceMembership.Role.MEMBER,
            is_active=False,
        )

        self.project = Project.objects.create(
            workspace=self.workspace,
            name="Dashboard project",
        )
        now = timezone.now()
        self.running_entry = TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.user,
            description="Running entry",
            start_time=now,
        )
        for index in range(5):
            started_at = now - timedelta(hours=index + 1)
            TimeEntry.objects.create(
                workspace=self.workspace,
                user=self.user,
                project=self.project,
                description=f"Finished entry {index}",
                start_time=started_at,
                end_time=started_at + timedelta(minutes=10),
            )
        TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.other_user,
            description="Another user's entry",
            start_time=now,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("workspaces:dashboard"))

        expected_url = f'{reverse("users:login")}?next={reverse("workspaces:dashboard")}'
        self.assertRedirects(response, expected_url)

    def test_dashboard_context_contains_only_current_user_data(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("workspaces:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/dashboard.html")
        workspaces = list(response.context["workspaces"])
        self.assertEqual(workspaces, [self.workspace])
        self.assertEqual(workspaces[0].member_count, 2)
        self.assertEqual(response.context["running_timer_count"], 1)

        recent_entries = list(response.context["recent_entries"])
        self.assertEqual(len(recent_entries), 5)
        self.assertEqual(recent_entries[0], self.running_entry)
        self.assertTrue(all(entry.user_id == self.user.pk for entry in recent_entries))

    def test_dashboard_renders_preview_lists_and_project_fallback(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("workspaces:dashboard"))

        self.assertContains(response, "Foundation Preview")
        self.assertContains(response, "read-only")
        self.assertContains(response, "Visible workspace")
        self.assertContains(response, "2 members")
        self.assertContains(response, "Running entry")
        self.assertContains(response, "No project")

    def test_dashboard_empty_states(self):
        empty_user = User.objects.create_user(mobile="09120000010")
        self.client.force_login(empty_user)

        response = self.client.get(reverse("workspaces:dashboard"))

        self.assertContains(response, "No workspaces yet.")
        self.assertContains(response, "No time entries yet.")

    def test_dashboard_link_is_visible_only_when_authenticated(self):
        landing_url = reverse("workspaces:landing")
        guest_response = self.client.get(landing_url)
        dashboard_url = reverse("workspaces:dashboard")

        self.assertNotContains(guest_response, f'href="{dashboard_url}"')

        self.client.force_login(self.user)
        user_response = self.client.get(landing_url)

        self.assertContains(user_response, f'href="{dashboard_url}"')
