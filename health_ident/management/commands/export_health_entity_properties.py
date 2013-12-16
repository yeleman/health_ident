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

from health_ident.models import HealthEntityProperty

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to export health_entity_properties to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['IDENT_Code', 'IDENT_PropertyName',
                   'IDENT_PropertyValue', 'IDENT_PropertyModifiedOn']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        print("Exporting Health Entity Properties...")


        for health_property in HealthEntityProperty.objects.all():
            property_dict = {}

            property_dict.update({
                'IDENT_Code': health_property.entity.slug,
                'IDENT_PropertyName': health_property.name,
                'IDENT_PropertyValue': health_property.value,
                'IDENT_PropertyModifiedOn': health_property.modified_on,
            })

            csv_writer.writerow(property_dict)
            print(health_property.entity.name)

        input_file.close()
