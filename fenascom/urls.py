#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.http import HttpResponse

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^/?$', 'fenascom.views.about', name='fenascom_about'),
    url(r'^browse/(?P<entity_slug>[a-zA-Z0-9]{3,6})/?$', 'fenascom.views.browser', name='fenascom_browser_at'),
    url(r'^browse/?$', 'fenascom.views.browser', name='fenascom_browser'),
    url(r'^map/?$', 'fenascom.views.map', name='fenascom_map'),
)
