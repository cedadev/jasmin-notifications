"""
Module containing helper functions for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from datetime import date

from .models import NotificationType, UserNotification, EmailNotification


def notify(notification_type, target, link, user = None, email = None):
    """
    Creates a notification with the given ``notification_type``, ``target`` and ``link``.

    ``notification_type`` can be given as a string.

    If ``user`` is given, a :py:class:`~.models.UserNotification` is created (even
    if ``email`` is also given), otherwise an :py:class:``~.models.EmailNotification``
    is created.
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
    notification.save()


def notify_if_not_exists(notification_type, target, link, user = None, email = None):
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
        notify(notification_type, target, link, user, email)


def notify_pending_deadline(deadline, deltas, notification_type, target,
                            link, user = None, email = None):
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
            notify(notification_type, target, link, user, email)
            return
