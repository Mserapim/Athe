# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Arquivo",
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
                ("filename", models.CharField(max_length=260, null=True, blank=True)),
                ("mimetype", models.CharField(max_length=100, null=True, blank=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("file", models.CharField(max_length=32)),
                (
                    "acesso",
                    models.PositiveIntegerField(
                        choices=[
                            (1, "PRIVADO"),
                            (2, "PRIVADO AO GRUPO"),
                            (3, "P\xdaBLICO"),
                        ]
                    ),
                ),
                (
                    "copia_de",
                    models.ForeignKey(
                        blank=True,
                        to="ged.Arquivo",
                        null=True,
                        on_delete=models.CASCADE,
                    ),
                ),  # Parametro "on_delete" adicionado. (Django 2)
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
