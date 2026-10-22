from django.contrib import admin
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.clients.admin import ClientAdmin
from apps.clients.models import Client
from apps.users.models import User
from apps.workspaces.models import Workspace


class ClientTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(mobile="09120000000")
        self.workspace = Workspace.objects.create(
            name="Test workspace",
            owner=owner,
        )

    def test_name_is_unique_among_active_clients_in_a_workspace(self):
        Client.objects.create(workspace=self.workspace, name="Quera")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Client.objects.create(workspace=self.workspace, name="Quera")

    def test_deleted_client_name_can_be_reused(self):
        client = Client.objects.create(workspace=self.workspace, name="Quera")
        client.delete()

        replacement = Client.objects.create(
            workspace=self.workspace,
            name="Quera",
        )

        self.assertNotEqual(replacement.pk, client.pk)
        self.assertEqual(
            list(Client.objects.filter(name="Quera")),
            [replacement],
        )
        self.assertEqual(Client.all_objects.filter(name="Quera").count(), 2)

    def test_admin_configuration(self):
        model_admin = ClientAdmin(Client, admin.site)

        self.assertEqual(model_admin.list_display, ("workspace", "name"))
        self.assertEqual(model_admin.search_fields, ("name",))
        self.assertEqual(model_admin.list_filter, ("workspace",))
        self.assertEqual(model_admin.ordering, ("-created_at",))
