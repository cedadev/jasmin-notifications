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


@require_safe
def follow(request, uuid):
    """
    Handler for ``/<uuid>/``.

    Responds to GET requests only.

    Marks all the notifications as read that have the same user and link before
    redirecting to the link.
    """
    # First, try to find a notification with the UUID
    notification = Notification.objects.filter(uuid = uuid).first()
    if not notification:
        raise http.Http404("Notification does not exist")
    if isinstance(notification, UserNotification):
        # For user notifications, the user must match the logged in user
        if request.user != notification.user:
            raise http.Http404("Notification does not exist")
        # Update the followed_at time for all the notifications for the same user
        # and link
        UserNotification.objects.filter(link = notification.link,
                                        user = notification.user,
                                        followed_at__isnull = True)  \
                                .update(followed_at = timezone.now())
    else:
        # For email notifications, just update this notification
        if not notification.followed_at:
            notification.followed_at = timezone.now()
        notification.save()
    return redirect(notification.link)
