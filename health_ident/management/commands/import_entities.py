#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.management import call_command

if PY2:
    import unicodecsv as csv
else:
    import csv

from health_ident.models import Entity, AdministrativeEntity, HealthEntity, EntityType

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to import from',
                    action='store',
                    dest='input_file'),
        make_option('-c',
                    help='Delete all Entity fixtures first',
                    action='store_true',
                    dest='clear')
    )

    def handle(self, *args, **options):

        headers = ['cls', 'slug', 'name', 'type_slug', 'parent_slug',
                   'latitude', 'longitude', 'health_center_ID',
                   'health_center_name', 'district']
        input_file = open(options.get('input_file'), 'r')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        if options.get('clear'):
            print("Removing all entities...")
            AdministrativeEntity.objects.all().delete()
            HealthEntity.objects.all().delete()
            Entity.objects.all().delete()
            print("Importing fixtures")
            call_command("loaddata", "fixtures/EntityType.xml")
            call_command("loaddata", "fixtures/Entity-root.xml")

        print("Importing entities...")

        for entry in csv_reader:
            if csv_reader.line_num == 1:
                continue

            cls = eval(entry.get('cls'))
            slug = entry.get('slug')
            name = entry.get('name')
            type_slug = entry.get('type_slug')
            entity_type = EntityType.objects.get(slug=type_slug)
            parent_slug = entry.get('parent_slug')
            latitude = entry.get('latitude')
            longitude = entry.get('longitude')
            health_center_id = entry.get('health_center_ID')
            if health_center_id:
                health_center = HealthEntity.objects.get(slug=health_center_id)
            else:
                health_center = None

            print(name, health_center)

            # entity =  cls.objects.get(slug=slug)

            entity = cls.objects.create(slug=slug,
                                        name=name,
                                        type=entity_type,
                                        latitude=latitude or None,
                                        longitude=longitude or None)
            if parent_slug:
                parentcls = Entity if parent_slug == 'mali' else cls
                parent = parentcls.objects.get(slug=parent_slug)
                entity.parent = parent

            if cls == AdministrativeEntity and health_center:
                entity.health_entity = health_center
                # entity.save()

            entity.save()
