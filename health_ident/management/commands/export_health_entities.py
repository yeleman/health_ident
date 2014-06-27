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

from health_ident.storage import IdentEntity


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

        mali = IdentEntity.get_or_none('mali')

        print("Exporting Health Entities...")

        for region in IdentEntity.find({'parent_code': 'mali'}):
            entities_slugs = []
            entities_slugs.append(region.code)
            for district in IdentEntity.find({'entity_type': 'health_district', 'parent_code': region.code}):
                entities_slugs.append(district.code)
                for health_area in IdentEntity.find({'entity_type': 'health_area', 'parent_code': 'district'}):
                    entities_slugs.append(health_area.code)
                    for health_center in IdentEntity.find({'entity_type': 'health_center', 'parent_code': 'health_area'}):
                        entities_slugs.append(health_center.code)
            # for entity in region.get_descendants(True):
            for entity_slug in entities_slugs:
                entity = IdentEntity.get_or_none(entity_slug)
                entity_dict = {}

                if entity.geometry:
                    geometry = entity.geojson
                else:
                    geometry = None

                entity_dict.update({
                    'IDENT_Code': entity.code,
                    'IDENT_Name': entity.name,
                    'IDENT_Type': entity.entity_type,
                    'IDENT_ParentCode': entity.parent_code,
                    'IDENT_MainEntityCode': entity.main_entity_code,
                    'IDENT_ModifiedOn': entity.modified_on.isoformat(),
                    'IDENT_Latitude': entity.latitude or "",
                    'IDENT_Longitude': entity.longitude or "",
                    'IDENT_Geometry': geometry or "",
                })

                if entity.entity_type == 'health_region':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.code})
                elif entity.entity_type == 'health_district':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.code,
                                        'IDENT_HealthDistrictCode': entity.code})
                elif entity.entity_type == 'health_area':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.parent.code,
                                        'IDENT_HealthDistrictCode': entity.parent.code,
                                        'IDENT_HealthAreaCode': entity.code})
                elif entity.entity_type == 'health_center':
                    entity_dict.update({'IDENT_HealthRegionCode': entity.parent.parent.parent.code,
                                        'IDENT_HealthDistrictCode': entity.parent.parent.code,
                                        'IDENT_HealthAreaCode': entity.parent.code})

                csv_writer.writerow(entity_dict)
                print(entity.name)

        input_file.close()
