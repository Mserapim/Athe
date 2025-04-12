# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0006_movimentacao_cache_rendered"),
    ]

    operations = [
        migrations.AddField(
            model_name="referencia",
            name="observation",
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="legalsign",
            name="content_sign",
            field=models.CharField(max_length=100, db_index=True),
            preserve_default=True,
        ),
    ]
