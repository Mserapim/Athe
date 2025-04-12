# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planoconta", "0005_provisionmanager_pension_system"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="provisionmanager",
            options={
                "ordering": (
                    "-reference_year",
                    "-reference_month",
                    "provision_plan",
                    "pension_system",
                )
            },
        ),
        migrations.AddField(
            model_name="plano",
            name="composes_total_net",
            field=models.BooleanField(
                default=False, verbose_name="Comp\xf5e l\xedquido?"
            ),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="finalidade",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="provisionmanager",
            name="pension_system",
            field=models.PositiveSmallIntegerField(
                default=1,
                verbose_name="Regime previdenci\xe1rio",
                choices=[(1, "RGPS"), (2, "RPPS"), (3, "MILITAR")],
            ),
        ),
        migrations.AlterField(
            model_name="provisionmanager",
            name="status",
            field=models.SmallIntegerField(
                default=1, verbose_name="Status", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="provisionplan",
            name="type_provision",
            field=models.IntegerField(),
        ),
    ]
