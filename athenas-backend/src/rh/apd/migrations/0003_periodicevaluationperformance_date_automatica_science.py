# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("apd", "0002_auto_20160825_1146"),
    ]

    operations = [
        migrations.AddField(
            model_name="periodicevaluationperformance",
            name="date_automatica_science",
            field=models.DateTimeField(
                null=True,
                verbose_name="Data da Ci\xeancia e Manifesta\xe7\xe3o Autom\xe1tica",
                blank=True,
            ),
        ),
    ]
