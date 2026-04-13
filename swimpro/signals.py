import asyncio
import sys

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .consumers import broadcast_session_change
from .models import TrainingSession


@receiver(post_save, sender=TrainingSession)
def session_saved(sender, instance, created, **kwargs):
    # Skip broadcasting if we are in a management command (like loaddata)
    # to prevent "no running event loop" errors.
    if len(sys.argv) > 1 and sys.argv[1] == 'loaddata':
        return

    action = 'created' if created else 'updated'

    try:
        # Check if there is a running event loop
        loop = asyncio.get_running_loop()
        asyncio.create_task(broadcast_session_change(instance, action))
    except RuntimeError:
        # No running loop (e.g., in sync context like loaddata or shell)
        # We simply skip the broadcast.
        # This is acceptable because fixtures are usually for setup, not live updates.
        pass


@receiver(post_delete, sender=TrainingSession)
def session_deleted(sender, instance, **kwargs):
    if len(sys.argv) > 1 and sys.argv[1] == 'loaddata':
        return

    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(broadcast_session_change(instance, 'deleted'))
    except RuntimeError:
        pass