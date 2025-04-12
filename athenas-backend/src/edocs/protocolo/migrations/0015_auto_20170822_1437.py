# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0014_movimentacao_physical"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attachment",
            name="observation",
            field=models.TextField(null=True, blank=True),
        ),
    ]
