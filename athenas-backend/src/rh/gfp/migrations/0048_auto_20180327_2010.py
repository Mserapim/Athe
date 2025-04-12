# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0047_auto_20180326_1935"),
        ("standard", "0007_auto_20180404_1937"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="transparencychoice",
            name="active1",
        ),
        migrations.AlterField(
            model_name="bankingconvenant",
            name="type_convenant",
            field=models.PositiveSmallIntegerField(
                default=2, verbose_name="Tipo Con\xeanio"
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="classification",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Classifica\xe7\xe3o"
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="employee_pays_pension",
            field=models.PositiveIntegerField(default=0, verbose_name="Pens\xe3o"),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="employee_source",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Tipo de servidor"
            ),
        ),
        migrations.AlterField(
            model_name="contracheque",
            name="status",
            field=models.PositiveIntegerField(
                default=1, verbose_name="Status", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estruturatabelasalarial",
            name="identifier",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="evento",
            name="base_de_calculo",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Base de c\xe1lculo"
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="carater",
            field=models.PositiveIntegerField(
                default=0, null=True, verbose_name="Car\xe1ter"
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="tipo_calculo",
            field=models.PositiveIntegerField(verbose_name="Tipo C\xe1lculo"),
        ),
        migrations.AlterField(
            model_name="extrapaymentperiod",
            name="type_value",
            field=models.SmallIntegerField(default=1, verbose_name="Tipo"),
        ),
        migrations.AlterField(
            model_name="folha",
            name="status",
            field=models.SmallIntegerField(
                default=1, verbose_name="Status", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="genreevent",
            name="character",
            field=models.PositiveIntegerField(
                default=0, null=True, verbose_name="Car\xe1ter"
            ),
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="status",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Status"),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Situa\xe7\xe3o"
            ),
        ),
        migrations.AlterField(
            model_name="paycheckdifferenceconfig",
            name="typeof",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Base"),
        ),
        migrations.AlterField(
            model_name="periodo",
            name="mes",
            field=models.PositiveIntegerField(verbose_name="M\xeas"),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="identifier",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Identificador"
            ),
        ),
        migrations.AlterField(
            model_name="previdencia",
            name="regime_previdenciario",
            field=models.PositiveSmallIntegerField(
                default=2, verbose_name="Regime previdenci\xc3\xa1rio"
            ),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao",
            field=models.SmallIntegerField(default=1, verbose_name="Gratif. Servidor"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_gratificacao_membro",
            field=models.SmallIntegerField(default=1, verbose_name="Gratif. Membro"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor",
            field=models.SmallIntegerField(default=1, verbose_name="Valor Servidor"),
        ),
        migrations.AlterField(
            model_name="referencianiveis2d",
            name="tipo_valor_membro",
            field=models.SmallIntegerField(default=1, verbose_name="Valor Membro"),
        ),
        migrations.AlterField(
            model_name="transparencychoice",
            name="group",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Grupos", blank=True
            ),
        ),
    ]
