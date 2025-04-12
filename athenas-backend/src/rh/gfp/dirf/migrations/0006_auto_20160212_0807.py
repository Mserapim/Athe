# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dirf", "0005_auto_20160211_1252"),
    ]

    operations = [
        migrations.AddField(
            model_name="declaracao",
            name="published",
            field=models.BooleanField(default=False, verbose_name=b"Publicado?"),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="declaracao",
            name="ano_base",
            field=models.IntegerField(default=2015, verbose_name=b"Ano base"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="declaracao",
            name="retificadora",
            field=models.IntegerField(default=1, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="demonstrativo",
            name="informacao_complementar",
            field=models.CharField(max_length=400, null=True),
            preserve_default=True,
        ),
    ]
