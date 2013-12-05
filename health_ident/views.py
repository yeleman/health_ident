#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render

from health_ident.models import HealthEntity, Entity, AdministrativeEntity


def browser(request, entity_slug=None):
    context = {"page": "browser"}
    health_center = False

    if entity_slug and not entity_slug == 'mali':
        entity = HealthEntity.objects.get(slug=entity_slug)
    else:
        entity = Entity.objects.get(slug="mali")

    context.update({'entity': entity})

    if entity.type.slug == 'health_center':
        health_center = True
        context.update({'villages': AdministrativeEntity.objects.filter(health_entity=entity)})

    context.update({'health_center': health_center})

    return render(request, "browser.html", context)


def map(request):
    context = {"page": "map"}
    health_entities = HealthEntity.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).filter(type__slug='health_center')
    context.update({'health_entities': health_entities,
                    'nb_centers_total': HealthEntity.objects.filter(type__slug='health_center').count(),
                    'nb_centers_nocoords': HealthEntity.objects.filter(type__slug='health_center', longitude__isnull=True, latitude__isnull=True).count(),})

    return render(request, "map.html", context)
