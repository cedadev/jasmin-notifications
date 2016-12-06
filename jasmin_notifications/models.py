"""
Django ORM models for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

import enum, uuid

from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template, TemplateDoesNotExist
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from polymorphic.models import PolymorphicModel
from polymorphic.manager import PolymorphicManager
from polymorphic.query import PolymorphicQuerySet

from picklefield.fields import PickledObjectField

from jasmin_django_utils.enumfield import EnumField
from jasmin_django_utils.crossdb import CrossDbGenericForeignKey

from .helpers import notify, notify_if_not_exists, notify_pending_deadline


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
        validators = [RegexValidator(regex = '^[a-zA-Z0-9_-]+$')],
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

    def clean(self):
        # Make sure that the required templates exist for the notification type
        if self.name:
            errors = []
            required_templates = [
                'jasmin_notifications/mail/{}/subject.txt'.format(self.name),
                'jasmin_notifications/mail/{}/content.txt'.format(self.name),
            ]
            if self.display:
                required_templates.append(
                    'jasmin_notifications/messages/{}.txt'.format(self.name),
                )
            for template in required_templates:
                try:
                    get_template(template)
                except TemplateDoesNotExist:
                    errors.append('Template {} does not exist'.format(template))
            if errors:
                raise ValidationError({ 'name' : errors })

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

    def delete(self, *args, **kwargs):
        # The default here raises an integrity error as the child entries are not
        # removed first
        for n in self: n.delete()


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
    #: Any extra context for template rendering
    extra_context = PickledObjectField(default = {})

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


class NotifiableUserMixin:
    """
    Mixin that provides notification methods for a user.
    """
    def notify(self, notification_type, target, link, **extra_context):
        """
        Creates a notification for this user with the given type, target and link.

        ``notification_type`` can be given as a string.

        Any additional ``kwargs`` are based as context variables for template rendering,
        both for emails and messages (if appropriate).
        """
        notify(notification_type, target, link, user = self, **extra_context)

    def notify_if_not_exists(self, notification_type, target, link, **extra_context):
        """
        Creates a notification for this user with the given type and target, only
        if such a notification does not already exist.

        See :py:meth:`notify` for more details.
        """
        notify_if_not_exists(notification_type, target, link, user = self, **extra_context)

    def notify_pending_deadline(self, deadline, deltas,
                                notification_type, target, link, **extra_context):
        """
        Ensures that a notification for this user of the given type and target
        is sent exactly once for each of the given ``deltas`` before the given
        ``deadline``.

        It is assumed that ``deltas`` are given in descending order, i.e. the longest
        delta first.
        """
        notify_pending_deadline(deadline, deltas, notification_type,
                                target, link, user = self, **extra_context)
