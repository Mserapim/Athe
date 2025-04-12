# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("patrimonio", "0004_auto_20151120_1134"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="grupocontabil",
            name="codigo_classificacao",
        ),
        migrations.RemoveField(
            model_name="grupocontabil",
            name="codigo_consolidacao",
        ),
        migrations.AddField(
            model_name="grupocontabil",
            name="cache_number",
            field=models.CharField(
                default="", unique=True, max_length=10, db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="grupocontabil",
            name="classificacao",
            field=models.CharField(default="", max_length=2),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="grupocontabil",
            name="consolidacao",
            field=models.CharField(default="", max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="grupocontabil",
            name="title",
            field=models.CharField(default="", max_length=80),
            preserve_default=False,
        ),
    ]
