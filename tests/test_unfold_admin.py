from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.test import SimpleTestCase
from unfold.admin import ModelAdmin, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from apps.users.admin import GroupAdmin, UserAdmin
from apps.users.models import User
from apps.workspaces.admin import WorkspaceMembershipInline
from core.admins.base import SoftDeleteAdmin
from core.admins.filters import SoftDeleteListFilter


class UnfoldAdminTests(SimpleTestCase):
    def test_unfold_is_loaded_before_django_admin(self):
        self.assertLess(
            settings.INSTALLED_APPS.index("unfold"),
            settings.INSTALLED_APPS.index("django.contrib.admin"),
        )

    def test_soft_delete_admin_uses_unfold_and_preserves_behaviour(self):
        self.assertTrue(issubclass(SoftDeleteAdmin, ModelAdmin))
        self.assertIn("soft_delete_selected", SoftDeleteAdmin.actions)
        self.assertIn("restore_selected", SoftDeleteAdmin.actions)
        self.assertIn("hard_delete_selected", SoftDeleteAdmin.actions)

        model_admin = SoftDeleteAdmin(User, admin.site)
        self.assertIn(SoftDeleteListFilter, model_admin.get_list_filter(None))

    def test_user_admin_uses_unfold_forms_and_django_behaviour(self):
        self.assertTrue(issubclass(UserAdmin, BaseUserAdmin))
        self.assertTrue(issubclass(UserAdmin, ModelAdmin))
        self.assertIs(UserAdmin.form, UserChangeForm)
        self.assertIs(UserAdmin.add_form, UserCreationForm)
        self.assertIs(UserAdmin.change_password_form, AdminPasswordChangeForm)

    def test_group_admin_is_registered_with_unfold(self):
        group_admin = admin.site._registry[Group]

        self.assertIsInstance(group_admin, GroupAdmin)
        self.assertIsInstance(group_admin, BaseGroupAdmin)
        self.assertIsInstance(group_admin, ModelAdmin)

    def test_workspace_membership_inline_uses_unfold(self):
        self.assertTrue(issubclass(WorkspaceMembershipInline, TabularInline))

    def test_unfold_branding_is_configured(self):
        self.assertEqual(settings.UNFOLD["SITE_TITLE"], "Quera Clock Admin")
        self.assertEqual(settings.UNFOLD["SITE_HEADER"], "Quera Clock")
        self.assertIn("Quera Clock", settings.UNFOLD["SITE_TITLE"])
