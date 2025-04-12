# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cif", "0016_teaching_modality"),
    ]

    operations = [
        migrations.AlterField(
            model_name="addresscif",
            name="type_residence",
            field=models.SmallIntegerField(
                default=0,
                null=True,
                verbose_name="Tipo de Resid\xeancia",
                blank=True,
                choices=[(1, "CASA"), (2, "APARTAMENTO"), (3, "HOTEL")],
            ),
        ),
    ]
