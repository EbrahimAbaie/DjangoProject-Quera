from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Workspace, WorkspaceMembership


@receiver(post_save, sender=Workspace)
def ensure_owner_membership(sender, instance, created, **kwargs):
    if created:
        WorkspaceMembership.objects.create(
            workspace=instance,
            user=instance.owner,
            role=WorkspaceMembership.Role.OWNER,
            is_active=True,
        )
