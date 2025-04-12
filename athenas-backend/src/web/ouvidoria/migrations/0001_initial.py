# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Manifestacao",
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
                (
                    "mora_no_municipio_referido",
                    models.CharField(
                        max_length=1, choices=[("S", "Sim"), ("N", "N\xe3o")]
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
    ]
