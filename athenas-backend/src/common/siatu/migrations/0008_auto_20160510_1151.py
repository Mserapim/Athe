# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("siatu", "0007_auto_20160510_1124"),
    ]

    operations = [
        migrations.AlterField(
            model_name="avaliacao",
            name="justificativa_netra",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="baseconhecimento",
            name="solucao",
            field=models.TextField(null=True, blank=True),
        ),
    ]
