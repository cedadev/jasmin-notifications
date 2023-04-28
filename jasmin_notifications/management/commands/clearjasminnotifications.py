import datetime

import django.core.management.base
import django.utils

from ... import models


class Command(django.core.management.base.BaseCommand):
    """Management command to cleanup JASMIN notifications."""

    help = "Cleanup old JASMIN notifications."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_followed = django.utils.timezone.now() - datetime.timedelta(days=365)  # 1 year.
        self.clean_unfollowed = django.utils.timezone.now() - datetime.timedelta(
            days=1826
        )  # 5 years.

    def handle(self, *args, **options):
        """Delete old notifications."""
        old_followed_notifications = models.Notification.objects.filter(
            followed_at__isnull=False, followed_at__lt=self.clean_followed
        )[:100]
        if old_followed_notifications:
            old_followed_notifications.delete()

        old_notifications = models.Notification.objects.filter(
            created_at__lt=self.clean_unfollowed
        )[:100]
        if old_notifications:
            old_notifications.delete()
