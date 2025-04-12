# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cirdir", "0006_auto_20190309_1339"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="controlinformation",
            options={
                "ordering": ["-year", "employee__pessoa_fisica__nome"],
                "verbose_name": "Controle de Informa\xe7\xf5es sobre Doc\xeancia, Resid\xeancia e Finan\xe7as",
                "permissions": (
                    ("can_management_member", "Pode gerenciar o CIRDIR dos Membros"),
                    (
                        "can_management_employee",
                        "Pode gerenciar o CIRDIR dos Servidores",
                    ),
                    (
                        "can_management_health_area",
                        "Pode gerenciar o Voc\xea \xe9 \xdanico",
                    ),
                ),
            },
        ),
    ]
