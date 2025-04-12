# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contrato", "0005_auto_20160510_0854"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acaocontrato",
            name="observacao",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="adtivo",
            name="observacao",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="dias_para_aviso",
            field=models.SmallIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="contrato",
            name="numero_pasta",
            field=models.CharField(default="", max_length=150, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="envionefornecedor",
            name="data_envio",
            field=models.DateField(
                null=True, verbose_name="Data envio fornecedor", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="medicao",
            name="fim_periodo_referencia",
            field=models.DateField(
                null=True, verbose_name="Fim do periodo de referencia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="medicao",
            name="inicio_periodo_referencia",
            field=models.DateField(
                null=True, verbose_name="Inicio do periodo referencia", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="medicao",
            name="observacao",
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="notaempenho",
            name="classificacao",
            field=models.IntegerField(
                blank=True,
                null=True,
                choices=[
                    (1, "Material de Consumo"),
                    (2, "Material Permanente"),
                    (3, "Servi\xe7os"),
                    (4, "Obras e Instala\xe7\xf5es"),
                ],
            ),
        ),
        migrations.AlterField(
            model_name="valorcontrato",
            name="data_ref_fim",
            field=models.DateField(
                null=True, verbose_name="Data Referencia Fim", blank=True
            ),
        ),
        migrations.AlterField(
            model_name="valorcontrato",
            name="data_ref_inicio",
            field=models.DateField(
                null=True, verbose_name="Data Referencia Inicio", blank=True
            ),
        ),
    ]
