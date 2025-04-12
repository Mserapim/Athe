# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketpay",
            name="types_recipes",
            field=models.CharField(
                default="", max_length=100, verbose_name="Tipos de Receita"
            ),
        ),
    ]
