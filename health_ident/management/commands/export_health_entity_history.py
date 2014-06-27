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

        headers = ['IDENT_Code', 'IDENT_IsActive', 'IDENT_Since']
        input_file = open(options.get('input_file'), 'w')
        csv_writer = csv.DictWriter(input_file, headers)

        csv_writer.writeheader()

        print("Exporting Health Entity Properties...")


        for entity in IdentEntity.find():
            if not len(entity.history):
                continue

            for history in entity.history:
                history_dict = {}

                history_dict.update({
                    'IDENT_Code': entity.code,
                    'IDENT_IsActive': history.get('active'),
                    'IDENT_Since': history.get('since').isoformat(),
                })

                csv_writer.writerow(history_dict)
                print(entity.name)

        input_file.close()
