# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0031_auto_20161121_1042"),
    ]

    operations = [
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="correct_contribution_base",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.AlterField(
            model_name="folhaevento",
            name="correct_employer_contribution",
            field=models.DecimalField(
                default=0, max_digits=16, decimal_places=2, blank=True
            ),
        ),
        migrations.RunSQL(
            migrations.RunSQL.noop, reverse_sql="SET CONSTRAINTS ALL IMMEDIATE"
        ),
    ]
