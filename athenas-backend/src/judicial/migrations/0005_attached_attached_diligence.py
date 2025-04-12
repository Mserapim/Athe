# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0004_auto_20160912_1645"),
    ]

    operations = [
        migrations.AddField(
            model_name="attached",
            name="attached_diligence",
            field=models.ForeignKey(
                related_name="attaches",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                to="judicial.Diligence",
                null=True,
            ),
        ),
    ]
