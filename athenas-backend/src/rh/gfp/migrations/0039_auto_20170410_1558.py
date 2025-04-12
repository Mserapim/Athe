# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0038_previdencia_identifier"),
    ]

    operations = [
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="information",
            field=models.CharField(
                default="", max_length=50, verbose_name="Info", blank=True
            ),
        ),
        migrations.AddField(
            model_name="extrapaymentperiod",
            name="type_value",
            field=models.SmallIntegerField(
                default=1,
                verbose_name="Tipo",
                choices=[(1, "MOEDA (R$)"), (2, "PERCENTUAL (%)")],
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="ano_calendario",
            field=models.PositiveIntegerField(
                verbose_name="Ano Calend\xe1rio", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador", choices=[(1, "PADR\xc3O")]
            ),
        ),
    ]
