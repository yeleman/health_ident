#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import template

from health_ident.storage import IdentEntity

register = template.Library()


@register.filter(name='hentities')
def only_health_entities(entities):
    return [h for h in entities if IdentEntity.find({'code': h.code, 'category': 'health'}).count()]


@register.filter(name='hnametype')
def type_formatted_name(entity):
    if entity.entity_type == 'country':
        return entity.name
    return "{type} de {entity}".format(type=IdentEntity.TYPES.get(entity.entity_type, "Entité"),
                                       entity=entity.name).upper()


@register.filter(name='villages')
def villages_for_hcenter(entity):
    return IdentEntity.find({'health_entity_code': entity.code})