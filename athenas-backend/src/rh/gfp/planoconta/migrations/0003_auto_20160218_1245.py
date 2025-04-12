# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("planoconta", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="provision",
            options={
                "ordering": (
                    "provision_manager__reference_year",
                    "provision_manager__reference_month",
                    "provision_employee__employee",
                )
            },
        ),
        migrations.AlterModelOptions(
            name="provisionemployee",
            options={"ordering": ("employee", "start_acquisition")},
        ),
        migrations.AlterModelOptions(
            name="provisionmanager",
            options={
                "ordering": ("-reference_year", "-reference_month", "provision_plan")
            },
        ),
        migrations.AlterField(
            model_name="plano",
            name="tipo",
            field=models.SmallIntegerField(
                choices=[(1, "CONSIGNA\xc7\xc3O"), (2, "L\xcdQUIDO"), (3, "PATRONAL")]
            ),
            preserve_default=True,
        ),
    ]
