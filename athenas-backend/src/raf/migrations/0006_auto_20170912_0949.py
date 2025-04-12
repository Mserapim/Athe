# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("raf", "0005_auto_20170905_0934"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dataeproc",
            options={
                "ordering": ["promotoria", "datamovimento"],
                "verbose_name": "DataEproc",
            },
        ),
        migrations.AddField(
            model_name="dataeproc",
            name="codmovimento",
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name="dataeproc",
            name="datamovimento",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
