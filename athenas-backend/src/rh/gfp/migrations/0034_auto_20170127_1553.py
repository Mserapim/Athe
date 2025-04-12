# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gfp", "0033_auto_20161129_1219"),
    ]

    operations = [
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="horizontal_labels",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="horizontal_name",
            field=models.CharField(default="REFER\xcaNCIA", max_length=20),
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="vertical_labels",
            field=models.CharField(default="", max_length=100),
        ),
        migrations.AddField(
            model_name="estruturatabelasalarial",
            name="vertical_name",
            field=models.CharField(default="CLASSE", max_length=20),
        ),
        migrations.AddField(
            model_name="referencianiveis2d",
            name="months_progression",
            field=models.PositiveSmallIntegerField(
                default=12, verbose_name="Progress\xf5es", blank=True
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
            name="meses_progressao",
            field=models.SmallIntegerField(
                default=12, verbose_name="Progress\xf5es", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estruturatabelasalarial",
            name="meses_progressao_inicial",
            field=models.SmallIntegerField(
                default=36, verbose_name="Progress\xf5es inicial", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="estruturatabelasalarial",
            name="modelo_tabela",
            field=models.ForeignKey(
                related_name="estruturas",
                verbose_name="Modelo",
                blank=True,
                to="gfp.ModeloTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
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
            model_name="genreevent",
            name="config_transparency",
            field=models.PositiveIntegerField(
                null=True, verbose_name="Portal Transpar\xeancia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="loadedentryhistory",
            name="status",
            field=models.PositiveSmallIntegerField(default=1, verbose_name="Status"),
        ),
        migrations.AlterField(
            model_name="modelotabelasalarial",
            name="labels_vertical",
            field=models.CharField(default="", max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name="paycheckdifference",
            name="status",
            field=models.PositiveSmallIntegerField(
                default=1, verbose_name="Situa\xe7\xe3o"
            ),
        ),
        migrations.AlterField(
            model_name="periodo",
            name="mes",
            field=models.PositiveIntegerField(verbose_name="M\xeas"),
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
            name="estrutura_salarial",
            field=models.ForeignKey(
                related_name="references",
                verbose_name="Estrutura Salarial",
                blank=True,
                to="gfp.EstruturaTabelaSalarial",
                null=True,
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="rraemployee",
            name="employee",
            field=models.ForeignKey(
                related_name="rra_references",
                verbose_name="Servidor",
                to="rh.Servidor",
                on_delete=models.CASCADE,
            ),  # Parametro "on_delete" adicionado. (Django 2)
        ),
        migrations.AlterField(
            model_name="transparencychoice",
            name="group",
            field=models.PositiveSmallIntegerField(
                null=True, verbose_name="Grupos", blank=True
            ),
        ),
    ]
