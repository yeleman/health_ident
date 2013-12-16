#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import zipfile

from django.conf import settings
from optparse import make_option
from django.core.management.base import BaseCommand
from django.template import loader, Context

from health_ident.models import Entity, HealthEntity


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-f',
                    help='CSV file to export health_entity_properties to',
                    action='store',
                    dest='input_file'),
    )

    def handle(self, *args, **options):

        export_dir = os.path.join(settings.BASE_DIR, 'j2me')

        mali = Entity.objects.get(slug='mali')

        print("Exporting Health Entities...")

        regions = HealthEntity.objects.filter(parent=mali)

        for region in regions:

            for district in region.get_children():

                district_file_content = loader.get_template("j2me/EntityHashTableDistrict.java") \
                                              .render(Context({'district': district}))

                with open(os.path.join(export_dir, "EntityHashTable{}.java".format(district.slug)), 'w') as f:
                    f.write(district_file_content.encode('utf-8'))

                print(district.name)

        with open(os.path.join(export_dir, "Utils.java"), 'w') as f:
            f.write(loader.get_template("j2me/Utils.java").render(Context({})).encode('utf-8'))

        with open(os.path.join(export_dir, "EntityHashTable.java"), 'w') as f:
            f.write(loader.get_template("j2me/EntityHashTable.java").render(Context({})).encode('utf-8'))


        region_file_content = loader.get_template("j2me/StaticCodes.java") \
                                    .render(Context({'regions': regions}))

        with open(os.path.join(export_dir, "StaticCodes.java"), 'w') as f:
            f.write(region_file_content.encode('utf-8'))

        zf = zipfile.ZipFile(options.get('input_file'), mode='w')
        for asset in os.listdir(os.path.join(export_dir)):
            zf.write(os.path.join(export_dir, asset),
                     os.path.join('snisi', 'entities', asset))
        zf.close()