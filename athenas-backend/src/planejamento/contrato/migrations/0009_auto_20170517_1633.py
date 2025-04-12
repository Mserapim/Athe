# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from standard.models import Choice


def fix_ordem(apps, schema_editor):
    for c in Choice.objects.filter(
        app_label__icontains="contrato",
        name__icontains="TIPO_ORDEM_CONTRATO",
        value__lt=100,
    ):
        Choice.objects.filter(id=c.id).update(value=int(c.value) + 100)


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0008_auto_20170201_1023"),
    ]

    operations = [
        migrations.AlterField(
            model_name="valorcontrato",
            name="tipo_valor_contrato",
            field=models.IntegerField(
                default=100,
                null=True,
                blank=True,
                choices=[(1, "Principal"), (2, "Prazo"), (3, "Valor"), (4, "Outros")],
            ),
        ),
        migrations.RunPython(fix_ordem),
    ]
