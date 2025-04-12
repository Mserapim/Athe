# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("raf", "0003_subitem_blocked"),
    ]

    operations = [
        migrations.AddField(
            model_name="autoreference",
            name="content_type",
            field=models.ForeignKey(
                blank=True,
                to="contenttypes.ContentType",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="autoreference",
            name="object_id",
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="dataeproc",
            name="ano_referencia",
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name="dataeproc",
            name="mes_referencia",
            field=models.CharField(max_length=2, null=True),
        ),
    ]
