#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

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
                   'IDENT_ModifiedOn',
                   'IDENT_HealthRegionCode', 'IDENT_HealthDistrictCode',
                   'IDENT_HealthAreaCode', 'IDENT_MainEntityCode',
                   'IDENT_Latitude', 'IDENT_Longitude', 'IDENT_Geometry']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        mali = Entity.objects.get(slug='mali')

        print("Exporting Health Entities...")

        for region in HealthEntity.objects.filter(parent=mali):
            entities_slugs = []
            entities_slugs.append(region.slug)
            for district in HealthEntity.objects.filter(type__slug='health_district', parent=region):
                entities_slugs.append(district.slug)
                for health_area in HealthEntity.objects.filter(type__slug='health_area', parent=district):
                    entities_slugs.append(health_area.slug)
                    for health_center in HealthEntity.objects.filter(type__slug='health_center', parent=health_area):
                        entities_slugs.append(health_center.slug)
            # for entity in region.get_descendants(True):
            for entity_slug in entities_slugs:
                entity = HealthEntity.objects.get(slug=entity_slug)
                entity_dict = {}

                if entity.geometry:
                    geometry = json.dumps(entity.geojson)
                else:
                    geometry = None

                entity_dict.update({
                    'IDENT_Code': entity.slug,
                    'IDENT_Name': entity.name,
                    'IDENT_Type': entity.type.slug,
                    'IDENT_ParentCode': getattr(entity.parent, 'slug') or "",
                    'IDENT_MainEntityCode': getattr(entity.main_entity, 'slug', "") or "",
                    'IDENT_ModifiedOn': entity.modified_on,
                    'IDENT_Latitude': entity.latitude or "",
                    'IDENT_Longitude': entity.longitude or "",
                    'IDENT_Geometry': geometry or "",
                })

                if entity.type.slug == 'health_region':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.slug})
                elif entity.type.slug == 'health_district':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.slug,
                                        'IDENT_HealthDistrictCode': entity.slug})
                elif entity.type.slug == 'health_area':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.parent.slug,
                                        'IDENT_HealthDistrictCode': entity.parent.slug,
                                        'IDENT_HealthAreaCode': entity.slug})
                elif entity.type.slug == 'health_center':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.parent.parent.slug,
                                        'IDENT_HealthDistrictCode': entity.parent.parent.slug,
                                        'IDENT_HealthAreaCode': entity.parent.slug})

                csv_writer.writerow(entity_dict)
                print(entity.name)

        input_file.close()
