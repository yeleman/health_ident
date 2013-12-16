#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.contrib import admin

from health_ident.models import (Entity, HealthEntity, AdministrativeEntity,
                                 HealthEntityProperty, EntityHistory)


class EntityAdmin(admin.ModelAdmin):

    list_display = ('slug', 'name', 'type', 'parent', 'parent_level')
    list_filter = ('type',)
    ordering = ('slug',)
    search_fields = ('slug', 'name')


admin.site.register(Entity, EntityAdmin)
admin.site.register(HealthEntity, EntityAdmin)
admin.site.register(AdministrativeEntity, EntityAdmin)
admin.site.register(EntityHistory)
admin.site.register(HealthEntityProperty)
