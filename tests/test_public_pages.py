from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tags.models import Tag
from apps.time_entries.models import TimeEntry
from apps.users.models import User
from apps.workspaces.models import Workspace


class PublicPageTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(mobile="09120000002")
        self.other_user = User.objects.create_user(mobile="09120000003")
        self.workspace = Workspace.objects.create(
            name="Quera",
            owner=self.owner,
        )
        self.client_record = Client.objects.create(
            workspace=self.workspace,
            name="Client",
        )
        self.project = Project.objects.create(
            workspace=self.workspace,
            client=self.client_record,
            name="Clock",
        )
        Tag.objects.create(workspace=self.workspace, name="Backend")

        started_at = timezone.now()
        TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.owner,
            project=self.project,
            start_time=started_at,
        )
        TimeEntry.objects.create(
            workspace=self.workspace,
            user=self.other_user,
            project=self.project,
            start_time=started_at,
            end_time=started_at + timedelta(minutes=15),
        )

    def test_landing_page_uses_named_route_template_and_counts(self):
        response = self.client.get(reverse("workspaces:landing"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/landing.html")
        self.assertEqual(response.context["workspace_count"], 1)
        self.assertEqual(response.context["project_count"], 1)
        self.assertContains(response, "1 workspaces")
        self.assertContains(response, reverse("workspaces:status"))

    def test_status_page_exposes_all_counts(self):
        response = self.client.get(reverse("workspaces:status"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/status.html")
        self.assertEqual(response.context["workspace_count"], 1)
        self.assertEqual(response.context["client_count"], 1)
        self.assertEqual(response.context["project_count"], 1)
        self.assertEqual(response.context["tag_count"], 1)
        self.assertEqual(response.context["time_entry_count"], 2)
        self.assertEqual(response.context["running_timer_count"], 1)

    def test_base_template_loads_static_css_and_navigation(self):
        response = self.client.get(reverse("workspaces:landing"))

        self.assertContains(response, "/static/css/app.css")
        self.assertContains(response, f'href="{reverse("workspaces:landing")}"')
        self.assertContains(response, f'href="{reverse("workspaces:status")}"')
