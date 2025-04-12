# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0033_auto_20161026_1544"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dadobancario",
            name="tipo_conta",
            field=models.IntegerField(
                verbose_name="Tipo de Conta",
                choices=[(1, "CORRENTE"), (2, "POUPAN\xc7A"), (3, "SAL\xc1RIO")],
            ),
        ),
        migrations.AlterField(
            model_name="dependencia",
            name="tipo",
            field=models.SmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="servidorlotacao",
            name="child_of",
            field=models.ForeignKey(
                related_name="father_of",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Derivada de",
                blank=True,
                to="rh.ServidorLotacao",
                null=True,
            ),
        ),
    ]
