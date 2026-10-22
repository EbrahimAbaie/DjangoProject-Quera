from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.clients.models import Client
from apps.projects.admin import ProjectAdmin
from apps.projects.models import Project
from apps.users.models import User
from apps.workspaces.models import Workspace


class ProjectTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(mobile="09121111111")
        self.first_workspace = Workspace.objects.create(
            name="First workspace",
            owner=owner,
        )
        self.second_workspace = Workspace.objects.create(
            name="Second workspace",
            owner=owner,
        )

    def test_client_must_belong_to_same_workspace(self):
        client = Client.objects.create(
            workspace=self.second_workspace,
            name="Quera",
        )
        project = Project(
            workspace=self.first_workspace,
            client=client,
            name="Clock",
        )

        with self.assertRaisesMessage(
            ValidationError,
            "Client must belong to the same workspace.",
        ):
            project.clean()

    def test_name_is_unique_among_active_projects(self):
        Project.objects.create(workspace=self.first_workspace, name="Clock")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Project.objects.create(workspace=self.first_workspace, name="Clock")

    def test_deleted_project_name_can_be_reused(self):
        project = Project.objects.create(
            workspace=self.first_workspace,
            name="Clock",
        )
        project.delete()

        replacement = Project.objects.create(
            workspace=self.first_workspace,
            name="Clock",
        )

        self.assertNotEqual(replacement.pk, project.pk)
        self.assertEqual(
            list(Project.objects.filter(name="Clock")),
            [replacement],
        )
        self.assertEqual(Project.all_objects.filter(name="Clock").count(), 2)

    def test_admin_configuration(self):
        model_admin = ProjectAdmin(Project, admin.site)

        self.assertEqual(
            model_admin.list_display,
            ("workspace", "name", "client", "is_archived"),
        )
        self.assertEqual(model_admin.search_fields, ("name",))
        self.assertEqual(model_admin.list_filter, ("workspace",))
        self.assertEqual(model_admin.ordering, ("-created_at",))
