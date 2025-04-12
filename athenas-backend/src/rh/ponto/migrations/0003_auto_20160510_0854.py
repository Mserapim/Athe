# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ponto", "0002_auto_20150810_1114"),
    ]

    operations = [
        migrations.AlterField(
            model_name="feriado",
            name="localidades",
            field=models.ManyToManyField(related_name="feriados", to="rh.Localidade"),
        ),
    ]
