"""
URL configuration for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

import django.urls

from . import views

app_name = "jasmin_notifications"
urlpatterns = [
    django.urls.re_path(
        r"^(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$",
        views.follow,
        name="follow",
    ),
    django.urls.path("clear_all/", views.clear_all, name="clear_all"),
]
