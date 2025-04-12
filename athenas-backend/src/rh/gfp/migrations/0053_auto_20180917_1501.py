# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0067_auto_20180917_1501"),
        ("gfp", "0052_auto_20180905_1920"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="incidence_suspensions",
            field=models.ManyToManyField(
                related_name="events",
                verbose_name="Suspens\xe3o de incid\xeancia",
                to="rh.ProcessSuspension",
            ),
        ),
    ]
