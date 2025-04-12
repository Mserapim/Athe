# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0031_auto_20160818_0946"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pessoa",
            name="slug",
            field=models.SlugField(
                default="", max_length=100, verbose_name="Slug", blank=True
            ),
        ),
        migrations.AlterUniqueTogether(
            name="dependencia",
            unique_together=set([]),
        ),
    ]
