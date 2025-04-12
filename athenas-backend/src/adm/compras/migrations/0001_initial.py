# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contabilidade", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="NEAquisicao",
            fields=[
                (
                    "ne_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="contabilidade.NE",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=("contabilidade.ne",),
        ),
        migrations.CreateModel(
            name="NEAquisicaoRegistroPreco",
            fields=[
                (
                    "ne_ptr",
                    models.OneToOneField(
                        parent_link=True,
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        to="contabilidade.NE",
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
                ("quantidade", models.IntegerField(default=0)),
            ],
            options={
                "db_table": "compras_neaquisicaorp",
            },
            bases=("contabilidade.ne",),
        ),
        migrations.CreateModel(
            name="NotaDotacao",
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
                ("numero", models.CharField(unique=True, max_length=50)),
                ("programa_trabalho", models.CharField(max_length=50)),
                ("valor", models.DecimalField(max_digits=16, decimal_places=2)),
                ("data", models.DateTimeField(null=True, blank=True)),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
