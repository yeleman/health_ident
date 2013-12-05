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

from health_ident.models import HealthEntity

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to import extra_data from (unified_malihealth_uuid_slug.csv)',
                    action='store',
                    dest='input_file'),
        make_option('-c',
                    help='Delete all Extra Data first',
                    action='store_true',
                    dest='clear')
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

        if options.get('clear'):
            print("Removing all extra data...")
            for entity in HealthEntity:
                entity.extra_data = None
                entity.save()

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
                    errors.append(entry)
                else:
                    entry.pop("antim_slug")
                    entity.extra_data = entry
                    entity.save()

        print(errors)
        print(len(errors))
