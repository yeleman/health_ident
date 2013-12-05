#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from django.shortcuts import render

from health_ident import get_last_export
from health_ident.models import HealthEntity, Entity, AdministrativeEntity


def about(request, entity_slug=None):
    context = {"page": "about"}

    last_export_date = get_last_export()
    suffix = last_export_date.strftime("%Y-%m-%d")
    output_file = "all_entities-{}.sqlite".format(suffix)
    output_sql = "all_entities-{}.sql".format(suffix)
    health_file = "health_entities-{}.csv".format(suffix)
    admin_file = "admin_entities-{}.csv".format(suffix)

    context.update(({'last_export_date': last_export_date,
                     'admin_entities_file': admin_file,
                     'health_entities_file': health_file,
                     'all_entities_file': output_file,
                     'all_entities_sql': output_sql}))

    all_admin = AdministrativeEntity.objects.all()
    all_health = HealthEntity.objects.all()

    context.update({
        'nb_cscom_total': all_health.filter(type__slug='health_center').count(),
        'nb_district_total': all_health.filter(type__slug='health_district').count(),
        'nb_village_total': all_admin.filter(type__slug='vfq').count(),
        'nb_commune_total': all_admin.filter(type__slug='commune').count(),
        'nb_cercle_total': all_admin.filter(type__slug='cercle').count(),
        'nb_village_alone': all_admin.filter(type__slug='vfq', health_entity__isnull=True).count(),
        'nb_village_nocoord': all_admin.filter(type__slug='vfq', latitude__isnull=True).count(),
        'nb_cscom_nocoord': all_health.filter(type__slug='health_center', latitude__isnull=True).count()
        })
    return render(request, "about.html", context)


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
