"""
Module defining views for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.views.decorators.http import require_safe
from django import http
from django.shortcuts import redirect
from django.utils import timezone

from .models import Notification, UserNotification


@require_safe
def follow(request, uuid):
    """
    Handler for ``/<uuid>/``.

    Responds to GET requests only.

    Marks the specified notification as read before redirecting to the link.
    """
    # First, try to find a notification with the UUID
    notification = Notification.objects.filter(uuid = uuid).first()
    # If the notification is a user notification, it must be for the logged in
    # user
    if isinstance(notification, UserNotification) and  \
       notification.user != request.user:
        notification = None
    if not notification:
        raise http.Http404("Notification does not exist")
    if not notification.followed_at:
        notification.followed_at = timezone.now()
    notification.save()
    return redirect(notification.link)
