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
                    help='CSV file to export admin_entities to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                   'IDENT_ModifiedOn', 'IDENT_RegionName', 'IDENT_CercleName',
                   'IDENT_CommuneName',
                   'IDENT_HealthAreaCode', 'IDENT_HealthAreaName',
                   'IDENT_HealthAreaCenterDistance',
                   'IDENT_Latitude', 'IDENT_Longitude', 'IDENT_Geometry']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        mali = IdentEntity.get_or_none('mali')

        print("Exporting Admin Entities...")

        for region in IdentEntity.find({'category': 'admin', 'parent_code': 'mali'}):
            for entity in region.get_descendants(True):
                entity = IdentEntity.get_or_none(entity.code)
                entity_dict = {}

                if entity.geometry:
                    geometry = json.dumps(entity.geojson)
                else:
                    geometry = None

                cercle_name = commune_name = None
                if entity.entity_type == 'cercle':
                    cercle_name = entity.name

                if entity.entity_type == 'commune':
                    cercle_name = entity.parent.name
                    commune_name = entity.name

                if entity.entity_type == 'vfq':
                    cercle_name = entity.parent.parent.name
                    commune_name = entity.parent.name

                entity_dict.update({
                    'IDENT_Code': entity.code,
                    'IDENT_Name': entity.name,
                    'IDENT_Type': entity.entity_type,
                    'IDENT_ParentCode': entity.parent_code,
                    'IDENT_ModifiedOn': entity.modified_on.isoformat(),
                    'IDENT_RegionName': region.name or "",
                    'IDENT_CercleName': cercle_name or "",
                    'IDENT_CommuneName': commune_name or "",
                    'IDENT_Latitude': entity.latitude or "",
                    'IDENT_Longitude': entity.longitude or "",
                    'IDENT_Geometry': geometry or "",
                })

                if entity.health_entity:
                    entity_dict.update({
                        'IDENT_HealthAreaCode': entity.health_entity_code,
                        'IDENT_HealthAreaName': entity.health_entity.name,
                        'IDENT_HealthAreaCenterDistance': entity.main_entity_distance,
                    })

                csv_writer.writerow(entity_dict)
                print(entity.name)

        input_file.close()
