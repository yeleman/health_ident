#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

from django.core.management.base import BaseCommand

from health_ident.storage import IdentEntity

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):

        def create_from_entity(health_center, parent_code, entity_type):

            code = "A{}".format(health_center.code)

            asaco = IdentEntity({
                'code': code,
                'name': health_center.name,
                'category': 'fenascom',
                'entity_type': entity_type,
                'parent_code': parent_code,
                'latitude': health_center.latitude,
                'longitude': health_center.longitude,
                'geometry': health_center.geometry,

                'health_entity_code': health_center.code,

                'properties': {},
            })

            asaco.save()

            return asaco

        # FENASCOM / Amali
        create_from_entity(IdentEntity.get_or_none("mali"), "", 'fenascom')

        # segou only for now
        regions = ['2732']

        for region_slug in regions:

            health_region = IdentEntity.get_or_none(region_slug)
            ferascom = create_from_entity(health_region,
                                          "A{}".format(health_region.parent.code),
                                          'ferascom')

            logger.info("{}: {}".format(ferascom.code, ferascom.name))

            for health_district in IdentEntity.find({
                    'entity_type': 'health_district',
                    'parent_code': region_slug
                }):

                felascom = create_from_entity(health_district,
                                              "A{}".format(health_district.parent.code),
                                              'felascom')

                logger.info("{}: {}".format(felascom.code, felascom.name))


                for health_area in IdentEntity.find({
                        'entity_type': 'health_area',
                        'parent_code': health_district.code
                    }):

                    health_center = IdentEntity.get_or_none(health_area.code[1:])

                    asaco = create_from_entity(health_center,
                                               "A{}".format(health_center.parent.parent.code),
                                               'asaco')

                    logger.info("{}: {}".format(asaco.code, asaco.name))

