# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0012_auto_20160215_1010"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="paycheckdifference",
            options={
                "ordering": ("-reference_year", "-reference_month", "employee", "event")
            },
        ),
    ]
