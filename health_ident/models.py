#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import json

from py3compat import implements_to_string
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager


def casted_entity(slug):
    try:
        return HealthEntity.objects.get(slug=slug)
    except HealthEntity.DoesNotExist:
        try:
            return AdministrativeEntity.objects.get(slug=slug)
        except AdministrativeEntity.DoesNotExist:
            return Entity.objects.get(slug=slug)


@implements_to_string
class EntityType(models.Model):

    class Meta:
        app_label = 'health_ident'
        verbose_name = _("Entity Type")
        verbose_name_plural = _("Entity Types")

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=30)

    def __str__(self):
        return self.name


@implements_to_string
class Entity(MPTTModel):

    class Meta:
        app_label = 'health_ident'
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")

    slug = models.SlugField(_("Slug"), max_length=15, primary_key=True)
    name = models.CharField(_("Name"), max_length=50)
    type = models.ForeignKey(EntityType, related_name='entities',
                             verbose_name=_("Type"))
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children',
                            verbose_name=_("Parent"))
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    geometry = models.TextField(blank=True, null=True)
    modified_on = models.DateTimeField(default=timezone.now)

    objects = TreeManager()

    def __str__(self):
        return self.name

    @property
    def geojson(self):
        return json.loads(self.geometry)

    def to_dict(self):
        return {'slug': self.slug,
                'name': self.name,
                'type': self.type.slug,
                'parent': getattr(self.parent, 'slug', None),
                'latitude': self.latitude,
                'longitude': self.longitude}

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
            code=self.slug, name=self.display_name())

    def parent_level(self):
        if self.parent:
            return self.parent.type
        # return self.parent
        return "NO PARENT"

    @property
    def gps(self):
        if self.latitude is not None and self.longitude is not None:
            return "{lat},{lon}".format(lat=self.latitude, lon=self.longitude)


class HealthEntity(Entity):

    class Meta:
        app_label = 'health_ident'
        verbose_name = _("Health Entity")
        verbose_name_plural = _("Health Entities")


class AdministrativeEntity(Entity):

    class Meta:
        app_label = 'health_ident'
        verbose_name = _("Admin. Entity")
        verbose_name_plural = _("Admin. Entities")

    health_entity = models.ForeignKey(HealthEntity, blank=True, null=True,
                                      related_name=_("admin_entities"))
    health_entity_distance = models.FloatField(blank=True, null=True)

    @property
    def distance(self):
        import math
        d = self.health_entity_distance
        if d is None:
            return None
        if d == math.floor(d):
            return int(d)
        return d

@implements_to_string
class EntityHistory(models.Model):

    entity = models.ForeignKey(HealthEntity, related_name='active_changes')
    active = models.BooleanField(default=True)
    since = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.entity


@implements_to_string
class HealthEntityProperty(models.Model):

    class Meta:
        app_label = 'health_ident'
        verbose_name = _("HealthEntity. Property")
        verbose_name_plural = _("HealthEntity. Properties")

    entity = models.ForeignKey(HealthEntity, related_name='properties')
    name = models.CharField(max_length=500)
    value = models.CharField(max_length=500)
    modified_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
