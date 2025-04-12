# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ponto", "0003_auto_20160510_0854"),
    ]

    operations = [
        migrations.AddField(
            model_name="falta",
            name="horas_negativas",
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
        migrations.AddField(
            model_name="falta",
            name="horas_positivas",
            field=models.DecimalField(default=0, max_digits=11, decimal_places=2),
        ),
    ]
