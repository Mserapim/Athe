# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0003_auto_20151022_0948"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="chamado",
            options={
                "ordering": ("nao_urgente", "-pk"),
                "permissions": (
                    ("admin", "Vis\xe3o administrativa"),
                    ("gerente", "Vis\xe3o de gerente"),
                    ("atendente", "Vis\xe3o de atendente"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="avaliacao",
            name="sugestao",
            field=models.CharField(max_length=2000, null=True),
            preserve_default=True,
        ),
    ]
