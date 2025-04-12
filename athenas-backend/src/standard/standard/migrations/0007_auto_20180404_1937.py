# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def copy_actives_from_transparencychoice(apps, schema_editor):
    TChoice = apps.get_model("gfp", "TransparencyChoice")
    Choice = apps.get_model("standard", "Choice")

    tcs = [t.pk for t in TChoice.objects.filter(active1=False)]

    ups = Choice.objects.filter(pk__in=tcs).update(active=False)
    print("UPDATEDS: %s" % ups)


def _null_function(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("standard", "0006_auto_20180402_1000"),
        ("gfp", "0047_auto_20180326_1935"),
    ]

    operations = [
        migrations.AddField(
            model_name="choice",
            name="active",
            field=models.BooleanField(default=True, verbose_name="Ativo?"),
        ),
        migrations.AddField(
            model_name="choice",
            name="order_weight",
            field=models.SmallIntegerField(
                default=0, verbose_name="Peso ordena\xc3\xa7\xc3\xa3o", blank=True
            ),
        ),
        migrations.RunPython(copy_actives_from_transparencychoice, _null_function),
    ]
