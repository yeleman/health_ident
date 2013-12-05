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

from health_ident.models import HealthEntity, Entity

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to export health_entities to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                   'IDENT_Active', 'IDENT_ActiveChangedOn', 'IDENT_ModifiedOn',
                   'IDENT_HealthRegionCode', 'IDENT_HealthDistricCode',
                   'Map Admin1', 'Map Admin2', 'Region', 'District',
                   'Facility Name', 'Facility_Type', 'Facility Type Recoded',
                   'Start Date', 'Accessibility', 'Source', 'Population',
                   'Village Number', 'Distance', 'Owner_Managing Authority',
                   'Lat', 'Long', 'LL_Source', 'Site_Notes', 'Category',
                   'uuid']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        mali = Entity.objects.get(slug='mali')

        print("Exporting Health Entities...")

        for region in HealthEntity.objects.filter(parent=mali):
            for entity in region.get_descendants(True):
                entity_dict = {}

                if entity.extra_data:
                    entity_dict.update(entity.extra_data)

                entity_dict.update({
                    'IDENT_Code': entity.slug,
                    'IDENT_Name': entity.name,
                    'IDENT_Type': entity.type.slug,
                    'IDENT_ParentCode': getattr(entity.parent, 'slug') or "",
                    'IDENT_Active': entity.active,
                    'IDENT_ActiveChangedOn': entity.active_changed_on,
                    'IDENT_ModifiedOn': entity.modified_on,
                })

                if entity.type.slug == 'health_region':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.slug})
                elif entity.type.slug == 'health_district':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.slug,
                                        'IDENT_HealthDistricCode': entity.slug})
                elif entity.type.slug == 'health_center':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.parent.slug,
                                        'IDENT_HealthDistricCode': entity.parent.slug})

                if entity.extra_data:
                    entity_dict.update(entity.extra_data)

                csv_writer.writerow(entity_dict)
                print(entity.name)

        input_file.close()