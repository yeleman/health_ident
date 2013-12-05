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

from health_ident.models import Entity, AdministrativeEntity

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to export admin_entities to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                   'IDENT_Active', 'IDENT_ActiveChangedOn', 'IDENT_ModifiedOn',
                   'IDENT_HealthCenterCode', 'IDENT_HealthCenterName']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        mali = Entity.objects.get(slug='mali')

        print("Exporting Admin Entities...")

        for region in AdministrativeEntity.objects.filter(parent=mali):
            for entity in region.get_descendants(True):
                entity = AdministrativeEntity.objects.get(slug=entity.slug)
                entity_dict = {}

                entity_dict.update({
                    'IDENT_Code': entity.slug,
                    'IDENT_Name': entity.name,
                    'IDENT_Type': entity.type.slug,
                    'IDENT_ParentCode': getattr(entity.parent, 'slug') or "",
                    'IDENT_Active': entity.active,
                    'IDENT_ActiveChangedOn': entity.active_changed_on,
                    'IDENT_ModifiedOn': entity.modified_on,
                })

                if entity.health_entity:
                    entity_dict.update({
                        'IDENT_HealthCenterCode': entity.health_entity.slug,
                        'IDENT_HealthCenterName': entity.health_entity.name,
                    })

                csv_writer.writerow(entity_dict)
                print(entity.name)

        input_file.close()
