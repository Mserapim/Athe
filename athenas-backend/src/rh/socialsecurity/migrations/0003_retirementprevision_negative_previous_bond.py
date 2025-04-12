# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0002_bootstrap"),
    ]

    operations = [
        migrations.AddField(
            model_name="retirementprevision",
            name="negative_previous_bond",
            field=models.BooleanField(
                default=False, verbose_name="Negativa de v\xednculo anterior"
            ),
            preserve_default=True,
        ),
    ]
