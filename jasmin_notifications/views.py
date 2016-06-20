"""
Module defining views for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.views.decorators.http import require_safe
from django import http
from django.shortcuts import redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .models import Notification, UserNotification


def _handle_notification(request, notification):
    if not notification.followed_at:
        notification.followed_at = timezone.now()
    notification.save()
    return redirect(notification.link)

@login_required
def _handle_user_notification(request, notification):
    # For user notifications, the user must match the logged in user
    if request.user != notification.user:
        raise http.Http404("Notification does not exist")
    return _handle_notification(request, notification)

@require_safe
def follow(request, uuid):
    """
    Handler for ``/<uuid>/``.

    Responds to GET requests only.

    Marks the specified notification as read before redirecting to the link.
    """
    # First, try to find a notification with the UUID
    notification = Notification.objects.filter(uuid = uuid).first()
    if not notification:
        raise http.Http404("Notification does not exist")
    # If we have a user notification, the user must match the logged in user
    if isinstance(notification, UserNotification):
        return _handle_user_notification(request, notification)
    else:
        return _handle_notification(request, notification)
