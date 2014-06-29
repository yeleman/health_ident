#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django.shortcuts import render

from health_ident.views import browser as ident_browser

logger = logging.getLogger(__name__)


def about(request):
    context = {"page": "about"}

    context.update({})

    return render(request, "fenascom/about.html", context)


def browser(request, entity_slug=None):
    if entity_slug is None:
        entity_slug = "Amali"

    return ident_browser(request, entity_slug,
                         template_name="fenascom/browser.html")


def map(request):
    context = {"page": "map"}

    return render(request, "fenascom/map.html", context)
