# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0015_auto_20160303_1737"),
    ]

    operations = [
        migrations.AddField(
            model_name="transparencychoice",
            name="active",
            field=models.BooleanField(default=False, verbose_name="Ativo"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                null=True, verbose_name="Portal Transpar\xeancia", blank=True
            ),
            preserve_default=True,
        ),
    ]
