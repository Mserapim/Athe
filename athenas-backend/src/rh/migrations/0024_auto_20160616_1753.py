# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0023_migrate_data_to_news_fields_phone_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orgaogeral",
            name="old",
            field=models.ForeignKey(
                related_name="new",
                verbose_name="\xd3rg\xe3o antigo",
                blank=True,
                to="rh.OrgaoGeral",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
    ]
