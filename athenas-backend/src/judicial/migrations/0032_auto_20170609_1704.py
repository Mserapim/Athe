# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0031_auto_20170529_1516"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="partlawsuit",
            options={
                "ordering": ("page_number", "created_at"),
                "permissions": (
                    ("can_sign", "Pode assinar qualquer documento"),
                    (
                        "can_sign_simples",
                        "Pode assinar qualquer documento classificado como simples",
                    ),
                ),
            },
        ),
        migrations.AlterField(
            model_name="partlawsuit",
            name="page_number",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
