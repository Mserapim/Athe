# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0007_auto_20160510_0854"),
    ]

    operations = [
        migrations.AddField(
            model_name="patrimonio",
            name="observacao",
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="tipo",
            field=models.SmallIntegerField(
                db_index=True,
                choices=[
                    (1, "Deprecia\xe7\xe3o de Rotina"),
                    (2, "Deprecia\xe7\xe3o manual"),
                    (3, "Reavalia\xe7\xe3o"),
                    (4, "Revers\xe3o de Deprecia\xe7\xe3o"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="movimentologstatus",
            name="atribuido_por",
            field=models.ForeignKey(
                related_name="+",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
