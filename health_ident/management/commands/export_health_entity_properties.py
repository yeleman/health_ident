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

from health_ident.storage import IdentEntity


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to export health_entity_properties to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        headers = ['IDENT_Code', 'IDENT_Namespace', 'IDENT_PropertyName',
                   'IDENT_PropertyValue', 'IDENT_PropertyModifiedOn']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        print("Exporting Health Entity Properties...")

        for entity in IdentEntity.find():

            for ns, nsdict in entity.properties.items():

                for prop_name, prop_dict in nsdict.items():

                    property_dict = {}

                    modified_on = prop_dict.get('modified_on')
                    property_dict.update({
                        'IDENT_Code': entity.code,
                        'IDENT_Namespace': ns,
                        'IDENT_PropertyName': prop_name,
                        'IDENT_PropertyValue': prop_dict.get('value'),
                        'IDENT_PropertyModifiedOn': modified_on.isoformat()
                        if modified_on else "",
                    })

                    csv_writer.writerow(property_dict)
                    print(entity.name)

        input_file.close()
