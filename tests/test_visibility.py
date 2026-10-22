from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from apps.clients.models import Client
from apps.projects.models import Project
from apps.tags.models import Tag
from apps.time_entries.models import TimeEntry
from apps.users.models import User
from apps.workspaces.models import Workspace, WorkspaceMembership
from apps.workspaces.permissions import (
    get_workspace_membership,
    get_workspace_role,
    has_workspace_role,
)


class VisibilityQuerySetTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(mobile="09125555555")
        self.member = User.objects.create_user(mobile="09126666666")
        self.other_user = User.objects.create_user(mobile="09127777777")

        self.visible_workspace = Workspace.objects.create(
            name="Visible",
            owner=self.owner,
        )
        self.inactive_workspace = Workspace.objects.create(
            name="Inactive",
            owner=self.owner,
        )
        self.deleted_membership_workspace = Workspace.objects.create(
            name="Deleted membership",
            owner=self.owner,
        )

        self.membership = WorkspaceMembership.objects.create(
            workspace=self.visible_workspace,
            user=self.member,
            role=WorkspaceMembership.Role.MEMBER,
        )
        WorkspaceMembership.objects.create(
            workspace=self.inactive_workspace,
            user=self.member,
            role=WorkspaceMembership.Role.MEMBER,
            is_active=False,
        )
        deleted_membership = WorkspaceMembership.objects.create(
            workspace=self.deleted_membership_workspace,
            user=self.member,
            role=WorkspaceMembership.Role.MEMBER,
        )
        deleted_membership.delete()

    def test_workspace_visibility_requires_enabled_membership(self):
        self.assertEqual(
            list(Workspace.objects.visible_to(self.member)),
            [self.visible_workspace],
        )
        self.assertFalse(Workspace.objects.visible_to(AnonymousUser()).exists())

    def test_membership_queryset_filters_enabled_memberships_for_user(self):
        self.assertEqual(
            list(WorkspaceMembership.objects.for_user(self.member)),
            [self.membership],
        )

    def test_workspace_models_are_visible_through_enabled_membership(self):
        visible_client = Client.objects.create(
            workspace=self.visible_workspace,
            name="Visible client",
        )
        Client.objects.create(
            workspace=self.inactive_workspace,
            name="Hidden client",
        )
        visible_project = Project.objects.create(
            workspace=self.visible_workspace,
            name="Visible project",
        )
        Project.objects.create(
            workspace=self.inactive_workspace,
            name="Hidden project",
        )
        visible_tag = Tag.objects.create(
            workspace=self.visible_workspace,
            name="Visible tag",
        )
        Tag.objects.create(
            workspace=self.inactive_workspace,
            name="Hidden tag",
        )

        self.assertEqual(list(Client.objects.visible_to(self.member)), [visible_client])
        self.assertEqual(
            list(Project.objects.visible_to(self.member)),
            [visible_project],
        )
        self.assertEqual(list(Tag.objects.visible_to(self.member)), [visible_tag])

    def test_not_archived_returns_only_unarchived_projects(self):
        active_project = Project.objects.create(
            workspace=self.visible_workspace,
            name="Active project",
        )
        Project.objects.create(
            workspace=self.visible_workspace,
            name="Archived project",
            is_archived=True,
        )

        self.assertEqual(list(Project.objects.not_archived()), [active_project])

    def test_time_entries_are_visible_only_to_their_user(self):
        own_entry = TimeEntry.objects.create(
            workspace=self.visible_workspace,
            user=self.member,
        )
        TimeEntry.objects.create(
            workspace=self.visible_workspace,
            user=self.other_user,
        )

        self.assertEqual(list(TimeEntry.objects.visible_to(self.member)), [own_entry])
        self.assertFalse(TimeEntry.objects.visible_to(AnonymousUser()).exists())


class WorkspacePermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(mobile="09128888888")
        self.member = User.objects.create_user(mobile="09129999999")
        self.outsider = User.objects.create_user(mobile="09120000001")
        self.workspace = Workspace.objects.create(name="Workspace", owner=self.owner)
        self.membership = WorkspaceMembership.objects.create(
            workspace=self.workspace,
            user=self.member,
            role=WorkspaceMembership.Role.MEMBER,
        )

    def test_membership_and_role_helpers(self):
        self.assertEqual(
            get_workspace_membership(self.member, self.workspace),
            self.membership,
        )
        self.assertEqual(get_workspace_role(self.owner, self.workspace), "owner")
        self.assertEqual(get_workspace_role(self.member, self.workspace), "member")
        self.assertIsNone(get_workspace_role(self.outsider, self.workspace))
        self.assertIsNone(get_workspace_membership(AnonymousUser(), self.workspace))

    def test_role_rank_comparison(self):
        self.assertTrue(has_workspace_role(self.owner, self.workspace, "admin"))
        self.assertTrue(has_workspace_role(self.member, self.workspace, "member"))
        self.assertFalse(has_workspace_role(self.member, self.workspace, "admin"))
        self.assertFalse(has_workspace_role(self.outsider, self.workspace, "member"))
