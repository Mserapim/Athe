# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0002_ticketpay_types_recipes"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketpay",
            name="process_number",
            field=models.CharField(
                default="0000000000000000000", max_length=25, verbose_name="Processo"
            ),
        ),
    ]
