"""
URL configuration for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.conf.urls import url, include

from . import views

app_name = 'jasmin_notifications'
urlpatterns = [
    url(
        r'^(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        views.follow,
        name = 'follow'
    ),
]
