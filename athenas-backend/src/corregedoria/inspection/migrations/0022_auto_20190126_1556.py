# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection", "0021_structureexternalpeoples"),
    ]

    operations = [
        migrations.AlterField(
            model_name="structureexternalpeoples",
            name="category",
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="structureexternalpeoples",
            name="function",
            field=models.CharField(max_length=300, null=True, blank=True),
        ),
    ]
