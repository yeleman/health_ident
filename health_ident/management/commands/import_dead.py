#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand

if PY2:
    import unicodecsv as csv
else:
    import csv

from health_ident.models import HealthEntity, HealthEntityProperty, EntityType

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to import extra_data from (unified_malihealth_uuid_slug.csv)',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['Map Admin1', 'Map Admin2', 'Region', 'District',
                   'Facility Name', 'Facility_Type', 'Facility Type Recoded',
                   'Start Date', 'Accessibility', 'Source', 'Population',
                   'Village Number', 'Distance', 'Owner_Managing Authority',
                   'Lat', 'Long', 'LL_Source', 'Site_Notes', 'Category',
                   'uuid', 'antim_slug']
        input_file = open(options.get('input_file'), 'r')
        csv_reader = csv.DictReader(input_file, fieldnames=headers)

        import unicodedata
        normalize_entity_name = lambda name: unicodedata.normalize('NFKD', unicode(name)).encode('ASCII', 'ignore').strip().upper()

        def find_at(level, name, parent=None):
            cls = HealthEntity
            tlevel = EntityType.objects.get(slug=level)
            tname = normalize_entity_name(name)
            try:
                fil = cls.objects.filter(type=tlevel, name=tname)
                if parent is not None:
                    fil = fil.filter(parent=parent)
                return fil.get()
            except Exception as e:
                children = cls.objects.filter(type=tlevel, parent=parent)
                for child in children:
                    if normalize_entity_name(child.name) == tname:
                        return child
                print(e)
                errtxt = "UNABLE TO MATCH /{}/. Possible Names:\n{}".format(tname, ", ".join([en.name for en in children]))
                raise ValueError(errtxt)

        print("Importing extra data...")

        errors = []

        for entry in csv_reader:
            if csv_reader.line_num == 1:
                continue

            entity_slug = entry.get('antim_slug')
            print(entity_slug)
            if entity_slug:
                try:
                    entity = HealthEntity.objects.get(slug=entity_slug)
                except HealthEntity.DoesNotExist:
                    region = find_at('health_region', entry.get('Region'))
                    district = find_at('health_district', entry.get('District'), parent=region)
                    entity = HealthEntity.objects.create(
                        slug=entity_slug,
                        name=normalize_entity_name(entry.get('Facility Name')),
                        type=EntityType.objects.get(slug='health_center'),
                        parent=district,
                        latitude=entry.get('Lat') or None,
                        longitude=entry.get('Long') or None)
                    for name, value in entry.items():
                        if name and value:
                            HealthEntityProperty.objects.create(
                                entity=entity,
                                name=name,
                                value=value)
                else:
                    entry.pop("antim_slug")

        print(errors)
        print(len(errors))
