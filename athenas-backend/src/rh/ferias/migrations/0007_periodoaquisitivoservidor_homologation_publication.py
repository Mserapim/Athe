# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0071_auto_20181205_2032"),
        ("ferias", "0006_datamigration"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
            name="homologation_publication",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Publica\xe7\xe3o de homologa\xe7\xe3o",
                blank=True,
                to="rh.Publicacao",
                null=True,
            ),
        ),
    ]
