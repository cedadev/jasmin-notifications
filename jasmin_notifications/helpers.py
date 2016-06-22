"""
Module containing helper functions for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from datetime import date

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from .models import NotificationType, UserNotification, EmailNotification


def notification_context(notification):
    """
    Takes a notification and returns a template context dictionary for that notification.

    This context dictionary will contain:

      * ``notification_type`` - the notification type as a string
      * ``level`` - the notification level as a string
      * ``email`` - the email that the notification is for
      * ``user`` - the user the notification is for, or ``None`` if the notification
                   is to an email that is not associated with a user
      * ``target`` - the target object for the notification
      * ``follow_link`` - the *fully qualified* link to follow the notification
      * ``created_at`` - the datetime at which the notification was created
      * ``followed_at`` - the datetime at which the notification was followed, or
                          ``None`` if it has not been followed
      * Any variables specified as ``extra_context``
    """
    if isinstance(notification, UserNotification):
        user = notification.user
        email = user.email
    else:
        # For email notifications, try to find a user with the email address to go
        # into the context
        email = notification.email
        user = get_user_model().objects.filter(email = email).first()
    # Create the context
    context = {
        'notification_type' : notification.notification_type.name,
        'level' : notification.notification_type.level.value,
        'email' : email,
        'user' : user,
        'target' : notification.target,
        'follow_link' : settings.BASE_URL + reverse(
            'jasmin_notifications:follow', kwargs = { 'uuid' : notification.uuid }
        ),
        'created_at' : notification.created_at,
        'followed_at' : notification.followed_at,
    }
    context.update(notification.extra_context)
    return context


def notify(notification_type, target, link, user = None, email = None, **extra_context):
    """
    Creates a notification with the given ``notification_type``, ``target`` and ``link``.

    ``notification_type`` can be given as a string.

    If ``user`` is given, a :py:class:`~.models.UserNotification` is created (even
    if ``email`` is also given), otherwise an :py:class:``~.models.EmailNotification``
    is created.

    Any additional ``kwargs`` are based as context variables for template rendering,
    both for emails and messages (if appropriate).
    """
    if not isinstance(notification_type, NotificationType):
        notification_type = NotificationType.objects.get(name = notification_type)
    if user:
        notification = UserNotification(user = user)
    elif email:
        notification = EmailNotification(email = email)
    else:
        raise ValueError('One of user or email must be given')
    notification.notification_type = notification_type
    notification.target = target
    notification.link = link
    notification.extra_context = extra_context
    notification.save()


def notify_if_not_exists(notification_type, target, link, user = None, email = None, **extra_context):
    """
    Creates a notification with the given ``notification_type``, ``target`` and
    ``email``\ /``user`` only if such a notification does not already exist.

    See :py:func:`notify` for more details.
    """
    if user:
        query = UserNotification.objects.filter(user = user)
    elif email:
        query = EmailNotification.objects.filter(email = email)
    else:
        raise ValueError('One of user or email must be given')
    if not query.filter_type(notification_type).filter_target(target).exists():
        notify(notification_type, target, link, user, email, **extra_context)


def notify_pending_deadline(deadline, deltas, notification_type, target,
                            link, user = None, email = None, **extra_context):
    """
    Ensures that a notification of the given type, target and email/user is sent
    exactly once for each of the given ``deltas`` before the given ``deadline``.

    It is assumed that ``deltas`` are given in descending order, i.e. the longest
    delta first.

    If ``user`` is present in ``kwargs``, :py:class:`~.models.UserNotification`\ s
    are created, otherwise :py:class:``~.models.EmailNotification``\ s are created.
    """
    # If the deadline has already passed, there is nothing to do
    today = date.today()
    if deadline < today:
        return
    # Work out whether we are using email or user notifications
    if user:
        query = UserNotification.objects.filter(user = user)
    elif email:
        query = EmailNotification.objects.filter(email = email)
    else:
        raise ValueError('One of user or email must be given')
    # Find the most recent notification for the type/target/recipient combo
    latest = query.filter_type(notification_type)  \
                  .filter_target(target)  \
                  .order_by('-created_at')  \
                  .first()
    for delta in deltas:
        threshold = deadline - delta
        # Deltas should be given longest first, so if we are before the threshold
        # for this delta, we are done
        if today <= threshold:
            return
        # Now we know threshold < today <= deadline
        # So send a notification unless one has already been sent in the window
        if not latest or latest.created_at.date() < threshold:
            notify(notification_type, target, link, user, email, **extra_context)
            return
