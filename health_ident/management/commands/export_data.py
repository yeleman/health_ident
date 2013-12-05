#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import datetime

import envoy
from py3compat import PY2
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from health_ident import get_last_export, set_last_export
from health_ident.models import Entity

if PY2:
    import unicodecsv as csv
else:
    import csv


class Command(BaseCommand):

    def handle(self, *args, **options):

        export_dir = os.path.join(settings.BASE_DIR, 'downloads')

        last_export = get_last_export()
        if last_export is not None:
            last_export_dt = datetime.datetime(last_export.year,
                                               last_export.month,
                                               last_export.day)
            last_export_dt = timezone.make_aware(last_export_dt, timezone.utc)

        if not last_export is None \
            and Entity.objects.order_by('-modified_on').last().modified_on <= last_export_dt:
            print("No modification")
            return 0

        today = datetime.date.today()
        suffix = today.strftime("%Y-%m-%d")
        output_file = os.path.join(export_dir, "all_entities-{0}.sqlite".format(suffix))
        output_sql = os.path.join(export_dir, "all_entities-{0}.sql".format(suffix))
        health_file = os.path.join(export_dir, "health_entities-{0}.csv".format(suffix))
        admin_file = os.path.join(export_dir, "admin_entities-{0}.csv".format(suffix))

        print("Exporting Health Entities")
        call_command("export_health_entities", input_file=health_file)

        print("Exporting Admin Entities")
        call_command("export_admin_entities", input_file=admin_file)

        print("Exporting Health Entities into SQLite")
        cmd = "csvsql --table 'health_entities' --insert --db 'sqlite:///{0}' {1}".format(output_file, health_file)
        envoy.run(cmd.encode('utf-8'))

        print("Exporting Admin Entities into SQLite")
        cmd = "csvsql --table 'admin_entities' --insert --db 'sqlite:///{0}' {1}".format(output_file, admin_file)
        envoy.run(cmd.encode('utf-8'))

        print("Dumping SQLite into an SQL file")
        cmd = "sqlite3 {0} .dump".format(output_file)
        r = envoy.run(cmd.encode('utf-8'))
        with open(output_sql, 'w') as f:
            f.write(r.std_out.decode('utf-8').encode('utf-8'))

        set_last_export(today)



