#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import datetime

LAST_EXPORT_PATH = 'last_export'


def get_last_export():
    try:
        with open(LAST_EXPORT_PATH, 'r') as f:
            return datetime.date(
                *[int(p) for p in f.read().strip().split("-")])
    except:
        return None


def set_last_export(adate):
    try:
        with open(LAST_EXPORT_PATH, 'w') as f:
            f.write(adate.strftime("%Y-%m-%d"))
        return True
    except:
        False
