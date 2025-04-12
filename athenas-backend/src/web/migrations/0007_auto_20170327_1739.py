# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("web", "0006_auto_20160510_0854"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="metakey",
            name="contents",
        ),
        migrations.RemoveField(
            model_name="metakey",
            name="key",
        ),
        migrations.AddField(
            model_name="metakey",
            name="name",
            field=models.CharField(
                default="", max_length=128, verbose_name="Chave", db_index=True
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="metakey",
            name="site",
            field=models.ForeignKey(
                related_name="metadata_keys",
                to="web.Area",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AddField(
            model_name="metakey",
            name="title",
            field=models.CharField(
                default="", max_length=128, verbose_name="T\xedtulo"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="metavalue",
            name="contents",
            field=models.ManyToManyField(
                related_name="metadata", verbose_name="Posts", to="web.Content"
            ),
        ),
        migrations.AlterField(
            model_name="metavalue",
            name="value",
            field=models.CharField(max_length=384, verbose_name="Valor", db_index=True),
        ),
    ]
