"""
Custom template tags for displaying unread notifications.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django import template
from django.urls import reverse

from ..helpers import notification_context
from ..models import UserNotification

register = template.Library()


@register.inclusion_tag("jasmin_notifications/notification_dropdown.html", takes_context=True)
def notification_dropdown(context):
    """
    Renders the notifications for the logged in user as a Bootstrap dropdown for
    inclusion in a navbar.

    The message for each notification is rendered using the template at
    ``jasmin_notifications/messages/{type}.html with the current notification context
    in scope. The context for each notification will be as returned by
    :py:func:`~.helpers.notification_context`.
    """
    # Get the logged in user from the context
    user = context.get("user")
    if user and user.is_authenticated:
        # Get the unread notifications for display for the user
        notifications = UserNotification.objects.filter(
            notification_type__display=True, user=user, followed_at__isnull=True
        ).order_by("-created_at")
    else:
        notifications = []
    # Convert the notifications into a more friendly dict for rendering
    notifications = [notification_context(n) for n in notifications]
    # Add in any extra notifications from the context
    notifications.extend(context.get("notifications_extra", []))
    return {
        "notifications": notifications,
    }
