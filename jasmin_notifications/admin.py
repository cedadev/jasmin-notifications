"""
Registration of models for the JASMIN account app with the admin interface.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.contrib import admin

from polymorphic.admin import (
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicChildModelFilter
)

from .models import NotificationType, Notification, EmailNotification, UserNotification


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')


@admin.register(EmailNotification)
class EmailNotificationAdmin(PolymorphicChildModelAdmin):
    base_model = EmailNotification

@admin.register(UserNotification)
class UserNotificationAdmin(PolymorphicChildModelAdmin):
    base_model = UserNotification

@admin.register(Notification)
class NotificationAdmin(PolymorphicParentModelAdmin):
    base_model = Notification
    child_models = (EmailNotification, UserNotification)
    polymorphic_list = True

    list_display = ('notification_type', 'level', 'email', 'uuid', 'followed_at', 'created_at')
    list_filter = ('notification_type', PolymorphicChildModelFilter)
    search_fields = ('notification_type__name', 'uuid', 'link',
                     'usernotification__user__username', 'usernotification__user__email',
                     'emailnotification__email', )

    def email(self, obj):
        if hasattr(obj, 'email'):
            return obj.email
        elif hasattr(obj, 'user'):
            return obj.user.email
        else:
            return None
    email.short_description = 'Email'

    def level(self, obj):
        return obj.notification_type.level.name
    level.short_description = 'Notification level'
