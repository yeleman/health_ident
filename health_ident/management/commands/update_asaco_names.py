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

        for asaco in IdentEntity.find({'entity_type': 'asaco'}):
            new_name = asaco.properties.get('fenascom', {}).get('NomASACO', {}).get('value')
            if new_name:
                asaco.name = new_name
                asaco.save()
                logger.info("Updated {}/{}".format(asaco.code, asaco.name))
