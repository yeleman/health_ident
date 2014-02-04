#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

from py3compat import PY2
from optparse import make_option
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone
from dateutil.parser import parse

if PY2:
    import unicodecsv as csv
else:
    import csv

from health_ident.models import (Entity, AdministrativeEntity,
                                 HealthEntity, EntityType,
                                 EntityHistory, HealthEntityProperty)

class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-a',
                    help='CSV file to import Administrative Entities from',
                    action='store',
                    dest='input_admin_file'),
        make_option('-f',
                    help='CSV file to import Health Entities from',
                    action='store',
                    dest='input_health_file'),
        make_option('-p',
                    help='CSV file to import Health Entity Properties from',
                    action='store',
                    dest='input_health_properties_file'),
        make_option('-c',
                    help='Delete all Entity fixtures first',
                    action='store_true',
                    dest='clear')
        )

    def handle(self, *args, **options):

        admin_headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                         'IDENT_ModifiedOn', 'IDENT_RegionName', 'IDENT_CercleName',
                         'IDENT_CommuneName',
                         'IDENT_HealthAreaCode', 'IDENT_HealthAreaName',
                         'IDENT_HealthAreaCenterDistance',
                         'IDENT_Latitude', 'IDENT_Longitude', 'IDENT_Geometry']

        health_headers = ['IDENT_Code', 'IDENT_Name', 'IDENT_Type', 'IDENT_ParentCode',
                          'IDENT_ModifiedOn',
                          'IDENT_HealthRegionCode', 'IDENT_HealthDistrictCode',
                          'IDENT_HealthAreaCode', 'IDENT_MainEntityCode',
                          'IDENT_Latitude', 'IDENT_Longitude', 'IDENT_Geometry']

        properties_headers = ['IDENT_Code', 'IDENT_PropertyName',
                              'IDENT_PropertyValue', 'IDENT_PropertyModifiedOn']

        input_admin_file = open(options.get('input_admin_file'), 'r')
        admin_csv_reader = csv.DictReader(input_admin_file, fieldnames=admin_headers)

        input_health_file = open(options.get('input_health_file'), 'r')
        health_csv_reader = csv.DictReader(input_health_file, fieldnames=health_headers)

        input_health_properties_file = open(options.get('input_health_properties_file'), 'r')
        health_properties_csv_reader = csv.DictReader(input_health_properties_file,
                                                      fieldnames=properties_headers)

        if options.get('clear'):
            print("Removing all entities...")
            AdministrativeEntity.objects.all().delete()
            HealthEntity.objects.all().delete()
            Entity.objects.all().delete()
            EntityHistory.objects.all().delete()
            HealthEntityProperty.objects.all().delete()
            print("Importing fixtures")
            call_command("loaddata", "fixtures/EntityType.xml")
            call_command("loaddata", "fixtures/Entity-root.xml")

        def add_entity(entity_dict, is_admin):
            cls = AdministrativeEntity if is_admin else HealthEntity
            slug = entry.get('IDENT_Code')
            name = entry.get('IDENT_Name')
            type_slug = entry.get('IDENT_Type')
            entity_type = EntityType.objects.get(slug=type_slug)
            parent_slug = entry.get('IDENT_ParentCode')
            latitude = entry.get('IDENT_Latitude')
            longitude = entry.get('IDENT_Longitude')
            geometry = entry.get('IDENT_Geometry')
            health_area_slug = entry.get('IDENT_HealthAreaCode')
            try:
                health_area_center_distance = float(entry.get('IDENT_HealthAreaCenterDistance'))
            except:
                health_area_center_distance = None
            if entity_type == 'vfq' and health_area_slug:
                health_area = HealthEntity.objects.get(slug=health_area_slug)
            else:
                health_area = None

            entity = cls.objects.create(slug=slug,
                                        name=name,
                                        type=entity_type,
                                        latitude=latitude or None,
                                        longitude=longitude or None,
                                        geometry=geometry or None)
            if parent_slug:
                parentcls = Entity if parent_slug == 'mali' else cls
                parent = parentcls.objects.get(slug=parent_slug)
                entity.parent = parent

            if cls == AdministrativeEntity and health_area:
                entity.health_entity = health_area
                if health_area_center_distance:
                    entity.main_entity_distance = health_area_center_distance

            entity.save()

            print(entity.name)

        print("Importing Health Entities...")
        for entry in health_csv_reader:
            if health_csv_reader.line_num == 1:
                continue

            add_entity(entry, False)

        print("Importing Admin Entities...")
        for entry in admin_csv_reader:
            if admin_csv_reader.line_num == 1:
                continue

            add_entity(entry, True)

        print("Updating Health Entities with main center")
        for entry in health_csv_reader:
            if health_csv_reader.line_num == 1:
                continue

            if not entry.get('IDENT_MainEntityCode'):
                continue

            entity = HealthEntity.objects.get(entry.get('IDENT_Code'))
            main_entity = HealthEntity.objects.get(entry.get('IDENT_MainEntityCode'))
            entity.main_entity = main_entity
            entity.save()

        print("Setting EntityHistory...")
        for entity in HealthEntity.objects.all():
            EntityHistory.objects.create(entity=entity, active=True)

        print("[MIGRATION] Setting HealthEntityProperty...")
        HealthEntityProperty.objects.all().delete()

        hc_only = ['Category', 'Facility Name', 'uuid', 'Distance',
                   'LL_Source', 'Facility Type Recoded', 'Start Date',
                   'Accessibility', 'Long', 'Facility_Type', 'Source', 'Lat']
        ha_only = ['Village Number', 'Population']
        both = ['Region', 'District', 'Map Admin2', 'Map Admin1']

        def _create(entity, entry):
            modified_on = parse(entry.get('IDENT_PropertyModifiedOn')).replace(tzinfo=timezone.utc)
            HealthEntityProperty.objects.create(
                entity=entity,
                name=entry.get('IDENT_PropertyName'),
                value=entry.get('IDENT_PropertyValue'),
                modified_on=modified_on)

        for entry in health_properties_csv_reader:
            if health_properties_csv_reader.line_num == 1:
                continue

            hc = HealthEntity.objects.get(slug=entry.get('IDENT_Code'))
            print(hc)
            try:
                ha = HealthEntity.objects.get(slug="Z{}".format(entry.get('IDENT_Code')))
            except HealthEntity.DoesNotExist:
                ha = None

            if entry.get('IDENT_PropertyName') in hc_only:
                _create(hc, entry)
            elif entry.get('IDENT_PropertyName') in ha_only and ha:
                _create(ha, entry)
            elif entry.get('IDENT_PropertyName') in both:
                if ha:
                    _create(ha, entry)
                _create(hc, entry)
            else:
                _create(hc, entry)

        # print("Importing Admin Entities...")
        # for entry in admin_csv_reader:
        #     if admin_csv_reader.line_num == 1:
        #         continue

        #     if entry.get('IDENT_HealthAreaCenterDistance'):
        #         entity = AdministrativeEntity.objects.get(slug=entry.get('IDENT_Code'))
        #         try:
        #             health_area_center_distance = float(entry.get('IDENT_HealthAreaCenterDistance'))
        #         except:
        #             health_area_center_distance = None
        #         entity.main_entity_distance = health_area_center_distance
        #         entity.save()


            # if entry.get('IDENT_HealthAreaCode'):
            #     entity = AdministrativeEntity.objects.get(slug=entry.get('IDENT_Code'))
            #     he = HealthEntity.objects.get(slug=entry.get('IDENT_HealthAreaCode'))
            #     entity.health_entity = he
            #     entity.save()



# def move_properties():
#     from health_ident.models import HealthEntity, HealthEntityProperty

#     def _try(hp, target_slug):
#         target = HealthEntity.objects.get(slug=target_slug)
#         try:
#             HealthEntityProperty.objects.create(
#                 entity=target,
#                 name=hp.name,
#                 value=hp.value,
#                 modified_on=hp.modified_on)
#         except:
#             pass

#     hc_only = ['Category', 'Facility Name', 'uuid', 'Distance',
#                'LL_Source', 'Facility Type Recoded', 'Start Date',
#                'Accessibility', 'Long', 'Facility_Type', 'Source', 'Lat']
#     ha_only = ['Village Number', 'Population']
#     both = ['Region', 'District', 'Map Admin2', 'Map Admin1']

#     for hp in HealthEntityProperty.objects.filter(name__in=hc_only):
#         if hp.entity.type.slug != 'health_center':
#             _try(hp, hp.entity.slug.replace(r'^Z', ''))
#             hp.delete()

#     for hp in HealthEntityProperty.objects.filter(name__in=ha_only):
#         if hp.entity.type.slug != 'health_area':
#             _try(hp, 'Z{}'.format(hp.entity.slug))
#             hp.delete()

#     for hp in HealthEntityProperty.objects.filter(name__in=both):
#         _try(hp, hp.entity.slug.replace(r'^Z', ''))
