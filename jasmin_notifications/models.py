"""
Django ORM models for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

import enum, uuid

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType

from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet

from jasmin_django_utils.enumfield import EnumField
from jasmin_django_utils.crossdb import CrossDbGenericForeignKey


@enum.unique
class NotificationLevel(enum.Enum):
    """
    Enum representing the levels that a notification can have.
    """
    #: A purely informational notification
    INFO = 'info'
    #: The notification indicates a user action is required
    ATTENTION = 'attention'
    #: The notification represents a success
    SUCCESS = 'success'
    #: The notification represents a warning
    WARNING = 'warning'
    #: The notification represents an error
    ERROR = 'error'


class NotificationType(models.Model):
    """
    Represents a notification type that an app may emit.
    """
    #: A short name for the notification type
    name = models.CharField(
        max_length = 50,
        help_text = 'A short name for the notification'
    )
    #: The level of the notification type
    level = EnumField(NotificationLevel)
    #: Indicates if notifications of this type should be displayed on the site
    #: Used for user notifications only
    display = models.BooleanField(
        default = True,
        help_text = 'Indicates of notifications of this type should be displayed '
                    'on site as well as emailed (user notifications only)'
    )

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, **defaults):
        """
        Shorthand for ``NotificationType.objects.update_or_create(...)``.
        """
        return cls.objects.update_or_create(name = name, defaults = defaults)


class NotificationQuerySet(PolymorphicQuerySet):
    """
    Custom queryset to allow filtering by target object.
    """
    def filter_target(self, target):
        return self.filter(
            target_ctype = ContentType.objects.get_for_model(target),
            target_id = target.pk
        )

    def filter_type(self, notification_type):
        if not isinstance(notification_type, NotificationType):
            notification_type = NotificationType.objects.get(name = notification_type)
        return self.filter(notification_type = notification_type)


class Notification(PolymorphicModel):
    """
    Represents a notification.
    """
    class Meta:
        get_latest_by = 'created_at'

    objects = NotificationQuerySet.as_manager()

    #: The UUID of the notification
    uuid = models.UUIDField(unique = True, default = uuid.uuid4, editable = False)
    #: The type of the notification
    notification_type = models.ForeignKey(NotificationType, models.CASCADE)
    #: Content type for notification target
    target_ctype = models.ForeignKey(ContentType, models.CASCADE)
    #: Object ID for notification target
    target_id = models.CharField(max_length = 250)
    #: The target object for the notification
    target = CrossDbGenericForeignKey('target_ctype', 'target_id')
    #: The onward link for the notification
    link = models.URLField()
    #: Datetime when the notification was created
    created_at = models.DateTimeField(auto_now_add = True)
    #: Datetime at which the notification was followed
    followed_at = models.DateTimeField(null = True, blank = True)

    @classmethod
    def create(cls, notification_type, **kwargs):
        """
        Creates a new notification. ``notification_type`` can be given as a string
        and will be converted.
        """
        if not isinstance(notification_type, NotificationType):
            notification_type = NotificationType.objects.get(name = notification_type)
        return cls.objects.create(notification_type = notification_type, **kwargs)

class EmailNotification(Notification):
    """
    Model for notifications sent to an email address with no attached user.
    """
    email = models.EmailField()

class UserNotification(Notification):
    """
    Model for notifications sent to a user.
    """
    #: The user being notified
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
