#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django import template

from health_ident.storage import IdentEntity

register = template.Library()


@register.filter(name='avillages')
def villages_for_asaco(entity):
    return IdentEntity.find({
        'entity_type': 'vfq',
        'health_entity_code': "Z{}".format(entity.code[1:])})


@register.filter(name='ahcenter')
def health_center_for_asaco(entity):
    return IdentEntity.get_or_none(entity.health_entity_code)


@register.filter(name='aharea')
def health_area_for_asaco(entity):
    return IdentEntity.get_or_none(
        "Z{}".format(health_center_for_asaco(entity).code))


@register.filter(name='ahdisrict')
def health_district_for_asaco(entity):
    return IdentEntity.get_or_none(entity.parent_code[1:])
