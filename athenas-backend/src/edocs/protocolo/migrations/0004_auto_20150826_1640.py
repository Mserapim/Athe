# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("protocolo", "0003_attachment_fill"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tipodocumento",
            options={"ordering": ("nome",)},
        ),
        migrations.AlterField(
            model_name="protocolo",
            name="resumo",
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
