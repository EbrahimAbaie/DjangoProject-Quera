import pytest
from django.contrib import admin
from django.db import IntegrityError, transaction

from apps.clients.admin import ClientAdmin
from apps.clients.models import Client
from apps.users.models import User
from apps.workspaces.models import Workspace


@pytest.fixture
def workspace(db):
    owner = User.objects.create_user(mobile="09120000000")
    return Workspace.objects.create(name="Test workspace", owner=owner)


@pytest.mark.django_db
def test_client_name_is_unique_among_active_clients_in_a_workspace(workspace):
    Client.objects.create(workspace=workspace, name="Quera")

    with pytest.raises(IntegrityError), transaction.atomic():
        Client.objects.create(workspace=workspace, name="Quera")


@pytest.mark.django_db
def test_deleted_client_name_can_be_reused(workspace):
    client = Client.objects.create(workspace=workspace, name="Quera")
    client.delete()

    replacement = Client.objects.create(workspace=workspace, name="Quera")

    assert replacement.pk != client.pk
    assert list(Client.objects.filter(name="Quera")) == [replacement]
    assert Client.all_objects.filter(name="Quera").count() == 2


def test_client_admin_configuration():
    model_admin = ClientAdmin(Client, admin.site)

    assert model_admin.list_display == ("workspace", "name")
    assert model_admin.search_fields == ("name",)
    assert model_admin.list_filter == ("workspace",)
    assert model_admin.ordering == ("-created_at",)
