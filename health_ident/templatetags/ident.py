#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import template

from health_ident.models import HealthEntity, AdministrativeEntity

register = template.Library()


@register.filter(name='hentities')
def only_health_entities(entities):
    return [h for h in entities if HealthEntity.objects.filter(slug=h.slug).count()]

@register.filter(name='hnametype')
def type_formatted_name(entity):
    if entity.type.slug == 'country':
        return entity.name
    return "{type} de {entity}".format(type=entity.type.name, entity=entity.name).upper()
