# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ferias", "0003_periodoaquisitivoservidorusufruto_suspenso_por"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodoaquisitivoservidor",
            name="paid_days",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Dias indenizados"
            ),
        )
    ]
