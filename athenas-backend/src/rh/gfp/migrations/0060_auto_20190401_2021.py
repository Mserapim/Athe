# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0080_auto_20190401_2020"),
        ("gfp", "0059_auto_20190130_1128"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evento",
            name="incidence_suspensions",
        ),
        migrations.AddField(
            model_name="evento",
            name="suspension_process",
            field=models.ManyToManyField(
                related_name="gfp_events", verbose_name="Eventos", to="rh.LegalProcess"
            ),
        ),
    ]
