# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_value_to_cvalue(apps, schema_editor):
    Choice = apps.get_model("standard", "Choice")
    ups = Choice.objects.filter(cvalue="").update(cvalue=models.F("value"))

    print("CHOICES UPDATEDS cvalue: %s" % ups)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0008_auto_20180426_1520"),
    ]

    operations = [
        migrations.AddField(
            model_name="choice",
            name="cvalue",
            field=models.CharField(
                default="",
                max_length=5,
                verbose_name="Identificador",
                db_index=True,
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="choice",
            name="value",
            field=models.SmallIntegerField(verbose_name="Valor", blank=True),
        ),
        migrations.RunPython(copy_value_to_cvalue, _null_function),
    ]
