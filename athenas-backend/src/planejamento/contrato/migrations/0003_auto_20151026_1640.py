# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AddField(
            model_name="contrato",
            name="numero_processo_mae",
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="valorcontrato",
            name="tipo_valor_contrato",
            field=models.IntegerField(
                default=1,
                null=True,
                blank=True,
                choices=[(1, "Principal"), (2, "Prazo"), (3, "Valor"), (4, "Outros")],
            ),
            preserve_default=True,
        ),
    ]
