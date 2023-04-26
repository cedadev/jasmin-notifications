import datetime

import django.core.management.base

from ... import models


class Command(django.core.management.base.BaseCommand):
    """Management command to cleanup JASMIN notifications."""

    help = "Cleanup old JASMIN notifications."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clean_followed = datetime.datetime.now() - datetime.timedelta(days=365)  # 1 year.
        self.clean_unfollowed = datetime.datetime.now() - datetime.timedelta(days=1826)  # 5 years.

    def handle(self, *args, **options):
        """Delete old notifications."""
        old_followed_notifications = models.Notification.objects.filter(
            followed_at__isnull=False, followed_at__lt=self.clean_followed
        )[:100]
        countf, _ = old_followed_notifications.delete()
        self.stdout.write(f"Deleted {countf} old followed notifications")

        old_notifications = models.Notification.objects.filter(
            created_at__lt=self.clean_unfollowed
        )[:100]
        counto, _ = old_notifications.delete()
        self.stdout.write(f"Deleted {counto} old.")
