# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.conf import settings
from django.core.management import call_command

import os

from rh.dayoff.models import AcquisitionPeriod, GroupPeriod

from rh.pvf.const import RESIDENTS_RECESS


def up(apps, schema_editor):
    print("Running forward...")

    for ap in AcquisitionPeriod.objects.filter(employee__type_by_possession="RES"):
        group_period = GroupPeriod.objects.filter(
            configuration__sub_type_of_usufruct=RESIDENTS_RECESS,
            year_reference=ap.start_date_acquisition.year,
        ).first()
        AcquisitionPeriod.objects.filter(pk=ap.pk).update(group_period=group_period)


def down(apps, schema_editor):
    print("Running backward...")


class Migration(migrations.Migration):

    dependencies = [("dayoff", "0033_auto_20230524_1324")]

    operations = [
        migrations.RunPython(up, down),
    ]
