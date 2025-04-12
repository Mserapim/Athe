# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Assunto",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("nome", models.CharField(max_length=200)),
            ],
            options={
                "ordering": ("nome",),
                "db_table": "epad_assunto",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Justificativa",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("valor_antigo", models.SmallIntegerField()),
                ("valor_novo", models.SmallIntegerField()),
                ("justificativa", models.TextField()),
                (
                    "tipo",
                    models.SmallIntegerField(
                        default=1, choices=[(1, "P\xe1gina"), (2, "Volume")]
                    ),
                ),
            ],
            options={
                "db_table": "epad_justificativa",
            },
            bases=(models.Model,),
        ),
    ]
