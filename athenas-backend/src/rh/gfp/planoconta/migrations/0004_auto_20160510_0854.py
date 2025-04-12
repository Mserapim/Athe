# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planoconta", "0003_auto_20160218_1245"),
    ]

    operations = [
        migrations.AlterField(
            model_name="plano",
            name="agencia",
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="plano",
            name="banco",
            field=models.ForeignKey(
                related_name="em_plano",
                blank=True,
                to="rh.Banco",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="plano",
            name="conta",
            field=models.CharField(max_length=15, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="evento_nld_two",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="planoconta",
            name="vpd",
            field=models.CharField(max_length=12, null=True, blank=True),
        ),
    ]
