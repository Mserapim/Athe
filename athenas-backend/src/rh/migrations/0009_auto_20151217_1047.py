# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0008_auto_20151210_1517"),
    ]

    operations = [
        migrations.AddField(
            model_name="cargo",
            name="instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Inst\xe2ncia",
                choices=[(1, "PRIMEIRA INST\xc2NCIA"), (2, "SEGUNDA INST\xc2NCIA")],
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="cargo",
            name="level_instance",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="Entr\xe2ncia",
                choices=[
                    (1, "PRIMEIRA ENTR\xc2NCIA"),
                    (2, "SEGUNDA ENTR\xc2NCIA"),
                    (3, "TERCEIRA ENTR\xc2NCIA"),
                    (4, "PROCURADORIA"),
                ],
            ),
            preserve_default=True,
        ),
    ]
