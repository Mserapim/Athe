# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0004_employmentbond_with_pgj"),
    ]

    operations = [
        migrations.AlterField(
            model_name="retirementprevision",
            name="contribution_prevision_date",
            field=models.DateField(
                null=True, verbose_name="Data da aposentadoria por contribui\xe7\xe3o"
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="retirementprevision",
            name="integral_prevision_date",
            field=models.DateField(
                null=True, verbose_name="Data da aposentadoria integral"
            ),
            preserve_default=True,
        ),
    ]
