#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand

from health_ident.storage import IdentEntity
from health_ident.models import (
    Entity, AdministrativeEntity, HealthEntity, casted_entity)


# def entity_by_slug(slug):
#     return entities.query.filter("obj.slug == @slug").bind(slug=slug).execute().first


class Command(BaseCommand):

    def handle(self, *args, **options):

        for level in range(5):
            for entity in Entity.objects.filter(level=level):
                entity = casted_entity(entity.slug)

                # logger.info("{}:    {}".format(level, entity))

                if not entity.name.strip():
                    continue

                is_admin = entity.__class__ == AdministrativeEntity
                is_health = entity.__class__ == HealthEntity

                # common fields
                entity_dict = {
                    'code': entity.slug,
                    'name': entity.name,
                    'category': 'entity' if entity.slug == 'mali' \
                                         else 'admin' if is_admin else 'health',
                    'entity_type': entity.type.slug,
                    'parent_code': getattr(entity.parent, 'slug', ''),
                    'latitude': entity.latitude,
                    'longitude': entity.longitude,
                    'geometry': entity.geojson or {},
                    'modified_on': entity.modified_on,
                }

                # class related fields
                if is_admin:
                    entity_dict.update({
                        'health_entity_code': getattr(entity.health_entity, 'slug', ''),
                        'main_entity_distance': entity.main_entity_distance,
                    })
                elif is_health:
                    entity_dict.update({
                        'main_entity_code': getattr(entity.main_entity, 'slug', '')
                    })

                # history
                if is_health:
                    entity_dict.update({
                        'history': [
                            {'active': h.active,
                             'since': h.since}
                            for h in entity.active_changes.all()
                        ]
                    })

                    # properties
                    entity_dict.update({
                        'properties': {
                            'default': {
                                p.name: {'value': p.value,
                                         'modified_on': p.modified_on}
                                for p in entity.properties.all()
                            }
                        }
                    })

                e = IdentEntity(entity_dict)
                e.save()
                logger.info("{}: {}".format(e._id, e.name))

                # doc = entities.documents.create(entity_dict)
                # logger.info(doc.id)

                # create edges
                # if doc.get('parent'):
                #     parent = entity_by_slug(doc.get('parent'))
                #     entities.edges.create(doc, parent)

                # if is_admin:
                #     health_entity = entity_by_slug(doc.get('health_entity'))
                #     entities.edges.create(doc, health_entity)

                # if is_health:
                #     main_entity = entity_by_slug(doc.get('main_entity'))
                #     entities.edges.create(doc, main_entity)
