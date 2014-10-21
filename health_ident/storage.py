#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import logging

import manga
from django.utils import timezone
from django.utils.translation import ugettext

logger = logging.getLogger(__name__)

manga.setup('health_ident')

SLUG_LEN = (4, 12)


class IdentEntity(manga.Model):

    TYPES = {
        'national': "National",
        'health_region': "Région",
        'health_district': "District",
        'health_area': "Aire Sanitaire",
        'health_center': "Unité Sanitaire",
        'private': "Privé",
        'asaco': "ASACO",
        'felascom': "FELASCOM",
        'ferascom': "FERASCOM",
        'fenascom': "FENASCOM"
    }

    code = manga.StringField(length=SLUG_LEN)
    name = manga.StringField(length=(2, 100))
    category = manga.StringField(length=(2, 10), default="entity")
    entity_type = manga.StringField(length=(2, 20))
    parent_code = manga.StringField(blank=True)
    latitude = manga.Field(blank=True)
    longitude = manga.Field(blank=True)
    geometry = manga.DictField(blank=True)
    modified_on = manga.DateTimeField(default=timezone.now)

    # only for admin
    health_entity_code = manga.StringField(blank=True)
    main_entity_distance = manga.Field(blank=True)

    # only for health
    main_entity_code = manga.StringField(blank=True)
    history = manga.ListField(default=[], blank=True)
    properties = manga.DictField(default={'default': {}}, blank=True)

    def __repr__(self):
        return "{code}/{name}".format(code=self.code, name=self.name)

    @property
    def geojson(self):
        if self.geometry is None:
            return None
        return self.geometry

    @classmethod
    def get_or_none(cls, code):
        return cls.find_one({'code': code})

    @property
    def parent(self):
        if self.parent_code:
            return self.find_one({'code': self.parent_code})
        return None

    @property
    def health_entity(self):
        if self.health_entity_code:
            return self.find_one({'code': self.health_entity_code})
        return None

    @property
    def main_entity(self):
        if self.main_entity_code:
            return self.find_one({'code': self.main_entity_code})
        return None

    def save(self, *args, **kwargs):
        self._id = self.code
        return super(IdentEntity, self).save(*args, **kwargs)

    def get_children(self):
        return IdentEntity.find({'parent_code': self.code})

    def get_ancestors(self):
        ancestors = []
        p = self
        while p.parent:
            p = p.parent
            ancestors.append(p)
        ancestors = reversed(ancestors)
        return ancestors

    def get_descendants(self, include_self=False):
        def recurs(e):
            d = []
            for child in e.get_children():
                d += [child]
                d += recurs(child)
            return d
        s = [self] if include_self else []
        return s + recurs(self)

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        if self.parent:
            return ugettext("{name}/{parent}").format(
                name=self.display_name(),
                parent=self.parent.display_name())
        return self.display_name()

    def display_code_name(self):
        return ugettext("{code}/{name}").format(
            code=self.code, name=self.display_name())

    @property
    def gps(self):
        if self.latitude is not None and self.longitude is not None:
            return "{lat},{lon}".format(lat=self.latitude, lon=self.longitude)
