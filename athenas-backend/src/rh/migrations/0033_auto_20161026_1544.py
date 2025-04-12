# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0032_auto_20160901_1253"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servidorlotacao",
            name="child_of",
            field=models.ForeignKey(
                related_name="father_of",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Derivada de",
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
    ]
