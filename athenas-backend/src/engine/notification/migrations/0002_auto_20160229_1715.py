# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="header",
            field=models.CharField(
                default="",
                help_text="",
                max_length=120,
                verbose_name="Header",
                blank=True,
            ),
            preserve_default=True,
        ),
    ]
