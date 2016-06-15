"""
Module containing helper functions for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from datetime import date

from .models import UserNotification, EmailNotification


def notify_if_not_exists(notification_type, target, **kwargs):
    """
    Creates a notification of the given type, target and email/user only if such
    a notification does not already exist.

    If ``user`` is present in ``kwargs``, a :py:class:`~.models.UserNotification`
    is created, otherwise an :py:class:``~.models.EmailNotification`` is created.
    """
    if 'user' in kwargs:
        klass = UserNotification
        query = UserNotification.objects.filter(user = kwargs['user'])
    elif 'email' in kwargs:
        klass = EmailNotification
        query = EmailNotification.objects.filter(email = kwargs['email'])
    else:
        raise ValueError('One of user or email must be given')
    if not query.filter_type(notification_type).filter_target(target).exists():
        klass.create(notification_type, target = target, **kwargs)


def notify_pending_deadline(deadline, deltas, notification_type, target, **kwargs):
    """
    Ensures that a notification of the given type, target and email/user is sent
    exactly once for each of the given ``deltas`` before the given ``deadline``.

    If ``user`` is present in ``kwargs``, :py:class:`~.models.UserNotification`\ s
    are created, otherwise :py:class:``~.models.EmailNotification``\ s are created.
    """
    # Work out whether we are using email or user notifications
    if 'user' in kwargs:
        klass = UserNotification
        query = UserNotification.objects.filter(user = kwargs['user'])
    elif 'email' in kwargs:
        klass = EmailNotification
        query = EmailNotification.objects.filter(email = kwargs['email'])
    else:
        raise ValueError('One of user or email must be given')
    # Find the most recent notification for the type/target/recipient combo
    latest = query.filter_type(notification_type)  \
                  .filter_target(target)  \
                  .order_by('-created_at')  \
                  .first()
    today = date.today()
    # Make sure the deltas are in order with the longest first
    for delta in deltas:
        # If we are in the window for the delta and no notification has been sent
        # within that window, send one
        threshold = deadline - delta
        if threshold <= today < deadline and  \
           (not latest or latest.created_at.date() < threshold):
            klass.create(notification_type, target = target, **kwargs)
            return
