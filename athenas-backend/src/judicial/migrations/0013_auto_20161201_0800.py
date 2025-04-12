# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0012_auto_20161130_1657"),
    ]

    operations = [
        migrations.AlterField(
            model_name="outcourtlawsuit",
            name="cache_number",
            field=models.CharField(max_length=20, verbose_name="N\xfamero/Ano"),
        ),
    ]
