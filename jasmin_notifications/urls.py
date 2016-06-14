"""
URL configuration for the JASMIN notifications app.
"""

__author__ = "Matt Pryor"
__copyright__ = "Copyright 2015 UK Science and Technology Facilities Council"

from django.conf.urls import url, include

from . import views

app_name = 'jasmin_notifications'
urlpatterns = [
    url(r'^(?P<uuid>[a-zA-Z0-9-]+)/$', views.follow, name = 'follow'),
]
