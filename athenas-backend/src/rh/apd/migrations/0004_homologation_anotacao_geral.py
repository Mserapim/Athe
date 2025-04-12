# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0046_auto_20170606_1554"),
        ("apd", "0003_periodicevaluationperformance_date_automatica_science"),
    ]

    operations = [
        migrations.AddField(
            model_name="homologation",
            name="anotacao_geral",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="Anota\xe7\xe3o Geral",
                blank=True,
                to="rh.AnotacaoGeral",
                null=True,
            ),
        ),
    ]
