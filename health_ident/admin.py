#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin

from health_ident.models import (Entity, HealthEntity, AdministrativeEntity,
                                 HealthEntityInfo)


admin.site.register(Entity)
admin.site.register(HealthEntity)
admin.site.register(AdministrativeEntity)
admin.site.register(HealthEntityInfo)
