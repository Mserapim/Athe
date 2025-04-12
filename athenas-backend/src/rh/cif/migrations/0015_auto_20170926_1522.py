# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0014_auto_20170829_1642"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addresscif",
            name="ref_address",
            field=models.ForeignKey(
                related_name="cif_address",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Endere\xe7o",
                blank=True,
                to="rh.Endereco",
                null=True,
            ),
        ),
    ]
