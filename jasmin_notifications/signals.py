"""
Module defining signal handlers for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

import logging

from django.conf import settings
from django.db.models import signals
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from .models import Notification, EmailNotification, UserNotification


_log = logging.getLogger(__name__)


@receiver(signals.post_save)
def send_notification(sender, instance, created, **kwargs):
    """
    When a new notification is created, send an email.

    The templates at ``jasmin_notifications/mail/{type}/{subject|content}.txt`` are
    rendered for the email subject and body. The following variables will be
    present in the template context:

      * ``notification_type`` - the notification type as a string
      * ``level`` - the notification level as a string
      * ``email`` - the email that the notification is for
      * ``user`` - the user the notification is for, or ``None`` if the notification
                   is to an email with no user
      * ``target`` - the target object for the notification
      * ``follow_link`` - the *fully qualified* link to follow the notification
      * ``notification`` - the notification itself
    """
    # Do nothing except for notifications
    if not isinstance(instance, Notification):
        return
    if created:
        if isinstance(instance, UserNotification):
            user = instance.user
            email = user.email
        else:
            email = instance.email
            user = get_user_model().objects.filter(email = instance.email).first()
        context = {
            'notification_type' : instance.notification_type.name,
            'level' : instance.notification_type.level.value,
            'email' : email,
            'user' : user,
            'target' : instance.target,
            'follow_link' : settings.BASE_URL +  \
                            reverse('jasmin_notifications:follow', kwargs = { 'uuid' : instance.uuid }),
            'notification' : instance,
        }
        template_dir = 'jasmin_notifications/mail/{}'.format(instance.notification_type.name)
        subject = render_to_string('{}/subject.txt'.format(template_dir), context)
        subject = (settings.EMAIL_SUBJECT_PREFIX + subject).strip()
        content = render_to_string('{}/content.txt'.format(template_dir), context)
        success = send_mail(
            subject = subject,
            message = content,
            from_email = settings.DEFAULT_FROM_EMAIL,
            recipient_list = [email],
            fail_silently = True
        )
        if not success:
            _log.error('Failed to send notification (uuid: {})'.format(instance.uuid))


@receiver(signals.post_delete)
def delete_notifications(sender, instance, **kwargs):
    """
    When an object is deleted, remove any notifications for it.
    """
    EmailNotification.objects.filter_target(instance).delete()
    UserNotification.objects.filter_target(instance).delete()
