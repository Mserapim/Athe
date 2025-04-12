# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0012_subitem_typesubitem"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="functionalactivityreport",
            options={
                "ordering": ["-year", "month"],
                "verbose_name": "RAF",
                "permissions": (("can_management_raf", "Pode gerenciar o RAF"),),
            },
        ),
        migrations.AlterField(
            model_name="subitem",
            name="typesubitem",
            field=models.PositiveSmallIntegerField(
                default=0,
                verbose_name="Tipo",
                choices=[
                    (0, "N\xe3o informado"),
                    (1, "Estat\xedstica/Quantidade"),
                    (2, "Movimentos"),
                ],
            ),
        ),
    ]
