# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="documentodigital",
            options={"verbose_name": "Documento Digital"},
        ),
        migrations.AddField(
            model_name="documentodigital",
            name="description",
            field=models.TextField(
                null=True, verbose_name="Descri\xe7\xe3o", blank=True
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="documentodigital",
            name="name",
            field=models.CharField(default="", max_length=100, verbose_name="Nome"),
            preserve_default=True,
        ),
    ]
