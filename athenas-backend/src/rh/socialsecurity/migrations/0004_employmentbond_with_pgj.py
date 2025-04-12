# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("socialsecurity", "0003_retirementprevision_negative_previous_bond"),
    ]

    operations = [
        migrations.AddField(
            model_name="employmentbond",
            name="with_pgj",
            field=models.BooleanField(
                default=False, verbose_name="V\xednculo com a PGJ"
            ),
            preserve_default=True,
        ),
    ]
