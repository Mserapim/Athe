# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("processo", "0005_auto_20170109_1445"),
    ]

    operations = [
        migrations.AddField(
            model_name="processo",
            name="classe_procedimento",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="processo",
            name="digito_verificador",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="processo",
            name="unidade_interna",
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name="processo",
            name="unidade_mp",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
