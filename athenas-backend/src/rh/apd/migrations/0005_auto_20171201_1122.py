# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apd", "0004_homologation_anotacao_geral"),
    ]

    operations = [
        migrations.AlterField(
            model_name="evaluation",
            name="days_suspended_evaluation",
            field=models.DecimalField(
                default=0, null=True, max_digits=11, decimal_places=2
            ),
        ),
    ]
