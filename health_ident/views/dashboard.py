#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)


from django.shortcuts import render


def dashboard(request):
    context = {"page": "dashboard"}
    return render(request, "dashboard.html", context)
