from django.contrib import admin
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.tags.admin import TagAdmin
from apps.tags.models import Tag
from apps.users.models import User
from apps.workspaces.models import Workspace


class TagTests(TestCase):
    def setUp(self):
        owner = User.objects.create_user(mobile="09122222222")
        self.workspace = Workspace.objects.create(name="Workspace", owner=owner)

    def test_name_is_unique_among_active_tags_in_a_workspace(self):
        Tag.objects.create(workspace=self.workspace, name="Important")

        with self.assertRaises(IntegrityError), transaction.atomic():
            Tag.objects.create(workspace=self.workspace, name="Important")

    def test_deleted_tag_name_can_be_reused(self):
        tag = Tag.objects.create(workspace=self.workspace, name="Important")
        tag.delete()

        replacement = Tag.objects.create(
            workspace=self.workspace,
            name="Important",
        )

        self.assertNotEqual(replacement.pk, tag.pk)
        self.assertEqual(list(Tag.objects.filter(name="Important")), [replacement])
        self.assertEqual(Tag.all_objects.filter(name="Important").count(), 2)

    def test_admin_configuration(self):
        model_admin = TagAdmin(Tag, admin.site)

        self.assertEqual(
            model_admin.list_display,
            ("workspace", "name", "color"),
        )
        self.assertEqual(model_admin.search_fields, ("name",))
        self.assertEqual(model_admin.list_filter, ("workspace",))
        self.assertEqual(model_admin.ordering, ("-created_at",))
